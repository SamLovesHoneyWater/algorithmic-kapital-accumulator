import pygame
import time, requests, sys
from datetime import datetime
from bs4 import BeautifulSoup

import json
import multiprocessing
import pandas as pd

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)


def get_stock_data(ticker):
    url = f'https://finance.yahoo.com/quote/{ticker}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        price_element = soup.find('fin-streamer', {'data-symbol': ticker, 'data-field': 'regularMarketPrice'})
        price = float(price_element.text.replace(',', '')) if price_element else None
        
        change_element = soup.find('fin-streamer', {'data-symbol': ticker, 'data-field': 'regularMarketChange'})
        change = float(change_element.text.replace(',', '')) if change_element else None
        
        pct_element = soup.find('fin-streamer', {'data-symbol': ticker, 'data-field': 'regularMarketChangePercent'})
        pct_change = float(pct_element.text.replace('%', '').replace('(', '').replace(')', '').replace(',', '')) if pct_element else None
        
        return {
            'symbol': ticker,
            'price': price,
            'time': time.time()
        }
        
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return None

def run_pygame(symbols, pipe_conn):
    # Initialize Pygame
    pygame.init()

    # Set up the display in full-screen mode
    screen_info = pygame.display.Info()
    screen_width, screen_height = screen_info.current_w, screen_info.current_h
    window_width, window_height = screen_width // 2, screen_height // 2
    screen = pygame.display.set_mode((window_width, window_height))
    WIDTH, HEIGHT = screen.get_size()
    pygame.display.set_caption("AKA Info Panel")
    
    # Fonts
    font = pygame.font.Font(None, 72)
    small_font = pygame.font.Font(None, 36)

    # Initialize variables
    clock = pygame.time.Clock()
    running = True
    dt = 1
    last_t = time.time()
    prices_df = pd.DataFrame(columns=['symbol', 'time', 'price'])

    while running:
        # Time to update data
        now = time.time()
        if now // dt > last_t // dt:
            # Update data if available
            if pipe_conn.poll():
                try:
                    received_data = pipe_conn.recv()  # Receive JSON data
                    for symbol, data in received_data.items():
                        if symbol not in symbols:
                            raise ValueError(f"Invalid symbol: {symbol}")
                        prices_df.loc[symbol] = [symbol, data['price']]
                        
                except Exception as e:
                    print(f"Error reading data from parent: {e}")
            # Init stage, just wait for first data to come in
            elif len(prices_df) == 0:
                time.sleep(dt / 10)
                continue
            # Otherwise, use the previous data
            


        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(BLACK)

        y_offset = 50
        # Render stock info
        for symbol in symbols:
            symbol_data = prices_df[prices_df['symbol'] == symbol]
            if not symbol_data.empty:
                # Plot line chart of prices vs. time
                times = symbol_data.index
                prices = symbol_data['price'].values

                if len(times) > 1:
                    max_price = max(prices)
                    min_price = min(prices)
                    price_range = max_price - min_price
                    if price_range == 0:
                        price_range = 1  # Avoid division by zero

                    scaled_prices = [(price - min_price) / price_range * (HEIGHT // 2) for price in prices]
                    scaled_times = [(time - times[0]).total_seconds() / (times[-1] - times[0]).total_seconds() * WIDTH for time in times]

                    points = list(zip(scaled_times, scaled_prices))
                    pygame.draw.lines(screen, GREEN, False, points, 2)


        # Render time
        current_datetime = "Thursday, January 09, 2025, 6 PM PST"
        current_datetime = datetime.now().strftime("%A, %B %d, %Y, %I:%M:%S %p %Z")
        datetime_surface = small_font.render(current_datetime, True, WHITE)
        datetime_rect = datetime_surface.get_rect(bottomright=(WIDTH - 10, HEIGHT - 10))
        screen.blit(datetime_surface, datetime_rect)

        pygame.display.flip()

        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    symbols = ["META", "IBM", "TSLA", "MSFT"]

    # Create a pipe for communication
    parent_conn, child_conn = multiprocessing.Pipe()

    # Start the Pygame process
    pygame_process = multiprocessing.Process(target=run_pygame, args=(symbols, child_conn,))
    pygame_process.start()

    # Send data to Pygame process
    try:
        while True:
            # Simulate real-time JSON updates
            data = {}
            for symbol in symbols:
                stock_data = get_stock_data(symbol)
                if stock_data:
                    data[symbol] = stock_data
            parent_conn.send(data)  # Send JSON data to the child process

            # Wait a bit before sending the next update
            time.sleep(1)

    except KeyboardInterrupt:
        print("Terminating Pygame process...")
        pygame_process.terminate()
        pygame_process.join()

