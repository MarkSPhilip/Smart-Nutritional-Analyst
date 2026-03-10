import json
import os
import re

class ParserAgent:
    def __init__(self):
        # Default weights for common items (used when no weight is specified)
        # Solids default to 100g, Eggs to 50g (1 unit), Liquids to 100ml
        self.default_weights = {
            'egg': 50,
            'eggs': 50,
        }
        self.liquids = {'milk', 'coffee', 'juice', 'water', 'soda', 'tea', 'protein shake', 'shake'}
        
        # Units to filter out from food name extraction
        self.unit_map = {
            'bowl': 250,
            'cup': 200,
            'glass': 250,
            'piece': 80,
            'slice': 40,
            'handful': 30,
            'small': 0.7, # multiplier
            'large': 1.5, # multiplier
            'tablespoon': 15,
            'teaspoon': 5,
            'plate': 400,
            'tbsp': 15,
            'tsp': 5,
        }
        # Numbers to filter out
        self.number_map = {
            'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
            '1': 1, '2': 2, '3': 3, '4': 4, '5': 5
        }
        # Filler words to ignore when extracting the "core" food name
        self.stop_words = {'a', 'an', 'the', 'some', 'had', 'ate', 'with', 'and', 'portions', 'of', 'for', 'full', 'is', 'was', 'were'}
        # Weight units to filter out from name
        self.weight_units = {'g', 'gm', 'gram', 'grams', 'ml', 'kg', 'mg', 'oz', 'lb'}

    async def parse(self, text: str):
        print(f"Agent A: Parsing input: {text}")
        items = []
        text_lower = text.lower()
        
        # Split by common separators
        segments = re.split(r',|and|with|\.|\n', text_lower)
        weight_pattern = re.compile(r'(\d+)\s*(gm|g|gram|ml|kg)?', re.IGNORECASE)
        
        for segment in segments:
            segment = segment.strip()
            if not segment: continue
            
            # 1. Detect Multiplier (two, 3, etc.)
            multiplier = 1
            for word, val in self.number_map.items():
                if re.search(r'\b' + word + r'\b', segment):
                    multiplier = val
                    break
            
            # 2. Detect Weight or Unit
            amount = None # Start with None to check if we need defaults later
            unit_found = False
            
            match = weight_pattern.search(segment)
            if match:
                val = int(match.group(1))
                unit = match.group(2)
                if unit == 'kg': val *= 1000
                amount = float(val)
                unit_found = True
            else:
                for unit, unit_weight in self.unit_map.items():
                    if re.search(r'\b' + unit + r'\b', segment):
                        if amount is None: amount = 100.0 # base for multiplier logic
                        if isinstance(unit_weight, float): # multiplier logic
                            amount *= unit_weight
                        else:
                            amount = float(unit_weight)
                        unit_found = True
                        break
            
            # 3. Dynamic Food Extraction
            # CRITICAL: Remove the weight/unit pattern from the segment text 
            # so it doesn't leave trailing 'g' or 'kg' in words (e.g. "chicken200g" -> "chicken")
            clean_segment = weight_pattern.sub('', segment)
            
            words = clean_segment.split()
            filtered_words = []
            for w in words:
                # Remove punctuation and numbers
                clean_w = re.sub(r'[^a-z]', '', w)
                if not clean_w: continue
                if clean_w in self.number_map: continue
                if clean_w in self.unit_map: continue
                if clean_w in self.stop_words: continue
                if clean_w in self.weight_units: continue
                filtered_words.append(clean_w)
            
            if filtered_words:
                food_candidate = " ".join(filtered_words)
                
                # 4. Apply Default Logic if no unit/weight was found
                if amount is None:
                    # Special Case: Coffee
                    if 'coffee' in food_candidate:
                        amount = 15.0 # 1 full tablespoon
                    # Case: Eggs
                    elif 'egg' in food_candidate:
                        amount = 50.0 # 1 egg = 50g
                    # Case: Liquids
                    elif any(l in food_candidate for l in self.liquids):
                        amount = 100.0 # 100ml
                    # Case: General Solids
                    else:
                        amount = 100.0 # 100g general default
                
                items.append({"name": food_candidate, "amount": amount * multiplier})
        
        if not items and text.strip():
            items.append({"name": "Unknown Item", "amount": 100.0})
            
        return items

import requests

class CalculatorAgent:
    def __init__(self):
        # OpenFoodFacts API base URL
        self.api_url = "https://world.openfoodfacts.org/cgi/search.pl"
        self.search_params = {
            "search_simple": 1,
            "action": "process",
            "json": 1,
            "page_size": 1
        }

    def calculate(self, parsed_items):
        print("Agent B: Calculating macros via OpenFoodFacts API...")
        total = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0}
        detailed_results = []

        for item in parsed_items:
            food_name = item["name"]
            amount = item["amount"]
            
            # Fetch from API
            params = self.search_params.copy()
            params["search_terms"] = food_name
            params["sort_by"] = "unique_scans_n" # Prioritize popular products
            
            try:
                response = requests.get(self.api_url, params=params, timeout=10)
                data = response.json()
                
                if data.get("products") and len(data["products"]) > 0:
                    # Baseline: start with the first product
                    selected_product = data["products"][0]
                    cals_per_100 = 0
                    prot_per_100 = 0
                    carb_per_100 = 0
                    fat_per_100 = 0
                    
                    # More robust macro extraction helper
                    def get_macro(nutriments, keys, default=None):
                        for k in keys:
                            val = nutriments.get(k)
                            if val is not None and val != "":
                                try:
                                    return float(val)
                                except (ValueError, TypeError):
                                    continue
                        return default

                    # Loop through up to 5 products to find one with actual nutritional data
                    for p in data["products"][:5]:
                        nutriments = p.get("nutriments", {})
                        
                        # Check if this product has energy data
                        cals = get_macro(nutriments, ["energy-kcal_100g", "energy-kcal"])
                        if cals is None:
                            kj = get_macro(nutriments, ["energy-kj_100g", "energy-kj"])
                            if kj:
                                cals = kj / 4.184
                        
                        # If we found calories > 0, we take this product
                        if cals and cals > 0:
                            selected_product = p
                            cals_per_100 = cals
                            prot_per_100 = get_macro(nutriments, ["proteins_100g", "proteins"], 0)
                            carb_per_100 = get_macro(nutriments, ["carbohydrates_100g", "carbohydrates"], 0)
                            fat_per_100 = get_macro(nutriments, ["fat_100g", "fat"], 0)
                            break
                    
                    # Final sanity check on selected product data if no energy was found above
                    if cals_per_100 == 0:
                        nutriments = selected_product.get("nutriments", {})
                        cals_per_100 = get_macro(nutriments, ["energy-kcal_100g", "energy-kcal"], 0)
                        prot_per_100 = get_macro(nutriments, ["proteins_100g", "proteins"], 0)
                        carb_per_100 = get_macro(nutriments, ["carbohydrates_100g", "carbohydrates"], 0)
                        fat_per_100 = get_macro(nutriments, ["fat_100g", "fat"], 0)

                    real_name = selected_product.get('product_name', food_name)
                    print(f"Agent B: Picked '{real_name}' for query '{food_name}'")
                    
                    ratio = amount / 100
                    item_results = {
                        "name": f"{food_name} ({real_name})",
                        "amount": amount,
                        "calories": round(float(cals_per_100) * ratio, 2),
                        "protein": round(float(prot_per_100) * ratio, 2),
                        "carbs": round(float(carb_per_100) * ratio, 2),
                        "fat": round(float(fat_per_100) * ratio, 2)
                    }
                    
                    for key in total:
                        total[key] += item_results[key]
                    
                    detailed_results.append(item_results)
                else:
                    print(f"Agent B: No product found for {food_name}")
                    detailed_results.append({
                        "name": f"{food_name} (Not found)",
                        "amount": amount,
                        "calories": 0, "protein": 0, "carbs": 0, "fat": 0
                    })
                    
            except Exception as e:
                print(f"Agent B Error fetching {food_name}: {e}")
                detailed_results.append({
                    "name": f"{food_name} (API Error)",
                    "amount": amount,
                    "calories": 0, "protein": 0, "carbs": 0, "fat": 0
                })

        # Round final totals
        for key in total:
            total[key] = round(total[key], 2)

        return {"total": total, "detailed_results": detailed_results}

class CoachAgent:
    def generate_feedback(self, total):
        print("Agent C: Generating feedback...")
        if total["calories"] == 0:
            return "Please enter a valid meal description to receive feedback."
        
        feedback = ""
        if total["protein"] < 15:
            feedback = "Your meal is a bit low in protein. Consider adding some Quark or Eggs next time to help with muscle recovery."
        elif total["calories"] > 800:
            feedback = "This was a very substantial meal! It provides plenty of energy, but watch out for calorie density if you're aiming for a deficit."
        else:
            feedback = "Excellent balanced choice! You're hitting a great mix of macros that will keep you satiated and energized."
        
        return feedback + " Keep up the great work on your nutrition journey!"
