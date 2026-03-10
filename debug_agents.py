import asyncio
import json
from agents import ParserAgent, CalculatorAgent

async def main():
    p = ParserAgent()
    c = CalculatorAgent()
    
    test_inputs = [
        "chicken200g",
        "two eggs",
        "coffee and milk",
        "300ml juice",
        "a tablespoon of coffee",
        "chicken breast"
    ]
    
    print("--- START DEBUG ---")
    for text in test_inputs:
        print(f"\nQUERY: {text}")
        parsed = await p.parse(text)
        print(f"  PARSED: {parsed}")
        result = c.calculate(parsed)
        for i, item in enumerate(parsed):
            calc_item = result["detailed_results"][i]
            print(f"  ITEM {i+1}: {item['name']} ({item['amount']}g)")
            print(f"  API MATCH: {calc_item['name']}")
            print(f"  MACROS: Cal:{calc_item['calories']}, P:{calc_item['protein']}, C:{calc_item['carbs']}, F:{calc_item['fat']}")
    print("--- END DEBUG ---")

if __name__ == "__main__":
    asyncio.run(main())
