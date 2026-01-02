from main import fetch_web_content

def test_web_fetch():
    """Test the web_fetch function with datatalks.club"""
    url = "https://datatalks.club"
    print(f"Fetching content from: {url}")
    print("-" * 80)

    try:
        content = fetch_web_content(url)
        print("SUCCESS! Content fetched:")
        print("-" * 80)
        print(content[:500])  # Print first 500 characters
        print("-" * 80)
        print(f"\nTotal length: {len(content)} characters")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_web_fetch()
