import cv2
import pytesseract
from PIL import Image
import mss, time
import re
from concurrent.futures import ThreadPoolExecutor
import matplotlib.pyplot as plt

pytesseract.pytesseract.tesseract_cmd = r'D:/Tesseract/tesseract.exe'

x0 = 1455
y0 = 1010
dx0 = 1605 - x0
dy = 1017 - 927
x1 = 1722
dx1 = 1861 - x1

# Serial solution (2.5 sec average)
def get_live_data_slow(tickers):
    images = []
    ocr_results = []
    parse_results = []

    for i, _ in enumerate(tickers):

        with mss.mss() as sct:
            # Ticker identification
            ticker_monitor = {"top": y0 - (i + 1) * dy, "left": x0, "width": dx0, "height": dy}
            ticker_screenshot = sct.grab(ticker_monitor)
            ticker_img = Image.frombytes("RGB", ticker_screenshot.size, ticker_screenshot.bgra, "raw", "BGRX")

            # Price identification
            price_monitor = {"top": y0 - (i + 1) * dy, "left": x1, "width": dx1, "height": dy//2 + 15}
            price_screenshot = sct.grab(price_monitor)
            price_img = Image.frombytes("RGB", price_screenshot.size, price_screenshot.bgra, "raw", "BGRX")

            images.append((ticker_img, price_img))
        # Step 2: Run OCR on the captured sidebar image
        ticker_text = pytesseract.image_to_string(ticker_img)
        price_text = pytesseract.image_to_string(price_img)

        # Step 3: Parse the OCR results
        '''
        if ticker in ticker_text:
            ticker_parse_success = True
        else:
            ticker_parse_success = False
        '''

        ticker = None
        for t in tickers:
            if t in ticker_text:
                # More than one ticker found, is erroneous
                if ticker is not None:
                    ticker = None
                    break
                ticker = t

        price_pattern = r'\$?\s*(\d+\.?\d*)'
        price_match = re.search(price_pattern, price_text)
        
        try:
            parsed_price = float(price_match.group(1)) if price_match else None
        except (AttributeError, ValueError):
            parsed_price = None
        
        ocr_results.append((ticker_text, price_text))
        parse_results.append((ticker, parsed_price))

        if not ticker or parsed_price is None:
            print(ocr_results)
            print(parse_results)
            display_pair(ticker_img, price_img)
    
    return parse_results

# Parallel solution (0.75 sec average)
def get_live_data(tickers: list[str]) -> list[tuple[str | None, float | None]]:
    def process_single_ticker(i):
        with mss.mss() as sct:
            ticker_monitor = {"top": y0 - (i + 1) * dy, "left": x0, "width": dx0, "height": dy}
            price_monitor = {"top": y0 - (i + 1) * dy, "left": x1, "width": dx1, "height": dy//2 + 15}
            
            ticker_screenshot = sct.grab(ticker_monitor)
            price_screenshot = sct.grab(price_monitor)
            
            ticker_img = Image.frombytes("RGB", ticker_screenshot.size, ticker_screenshot.bgra, "raw", "BGRX")
            price_img = Image.frombytes("RGB", price_screenshot.size, price_screenshot.bgra, "raw", "BGRX")
            
            ticker_text = pytesseract.image_to_string(ticker_img)
            price_text = pytesseract.image_to_string(price_img)
            
            #ticker_parse_success = ticker in ticker_text
            ticker = None
            for t in tickers:
                if t in ticker_text:
                    # More than one ticker found, is erroneous
                    if ticker is not None:
                        ticker = None
                        break
                    ticker = t
            
            price_pattern = r'\$?\s*(\d+\.?\d*)'
            price_match = re.search(price_pattern, price_text)
            
            try:
                parsed_price = float(price_match.group(1)) if price_match else None
            except (AttributeError, ValueError):
                parsed_price = None

            return ticker, parsed_price
            #return ticker_parse_success, parsed_price

    # Execute in parallel
    with ThreadPoolExecutor() as executor:
        #results = list(executor.map(process_single_ticker, enumerate(tickers)))
        results = list(executor.map(process_single_ticker, range(len(tickers))))
        
    return results


def display_pair(ticker_img, price_img):
    fig, ax = plt.subplots(1, 2, figsize=(12, 6))
    ax[0].imshow(ticker_img)
    ax[0].axis('off')
    ax[1].imshow(price_img)
    ax[1].axis('off')
    plt.show()

if __name__ == '__main__':
    tickers = ["META", "IBM", "TSLA", "MSFT"]
    t0 = time.time()
    parse_results = get_live_data_slow(tickers)
    t1 = time.time()
    print(f"Time taken: {t1 - t0:.2f} seconds")
    print(parse_results)

    times = []
    for _ in range(10):
        t0 = time.time()
        parse_results = get_live_data(tickers)
        t1 = time.time()
        times.append(t1 - t0)
        #print(parse_results)
        for i in range(len(tickers)):
            if not parse_results[i][0] or parse_results[i][1] is None:
                print("Failed to parse")

    avg_time = sum(times) / len(times)
    print(f"Average time: {avg_time:.2f} seconds")

    plt.figure(figsize=(8, 4))
    plt.hist(times, bins=5)
    plt.title('Distribution of Processing Times')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Frequency')
    plt.show()
