from engine.ai_engine import run_ai
from automation.scraper import get_trends
from automation.monetizer import generate_product
from automation.publisher import publish

def main():
    print("🌌 KARLFINE GOD MODE RUNNING")
    while True:
        trends = get_trends()
        product = generate_product(trends)
        publish(product)

        user = input(">> ")
        if user == "exit":
            break

        print(run_ai(user))

if __name__ == "__main__":
    main()
