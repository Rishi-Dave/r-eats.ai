from openai import AzureOpenAI
import openai
import json
from typing import List, Dict
import os
import dotenv

dotenv.load_dotenv()

client = AzureOpenAI(
  azure_endpoint = os.environ["AZURE_OPENAI_ENDPOINT"], 
  api_key=os.environ['AZURE_OPENAI_API_KEY'],  
  api_version = "2024-12-01-preview"
)
deployment= "gpt-35-turbo"

# --- Load your restaurant data (replace with your actual loading mechanism) ---
def load_restaurant_data(filepath="riverside_restaurants_fixed.json"):
    """Loads the structured natural language data for restaurants."""
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return []

restaurant_data: List[Dict] = load_restaurant_data()

# --- Function to retrieve relevant restaurants (basic keyword search for now) ---
def retrieve_relevant_restaurants(query: str, data: List[Dict], top_n: int = 5) -> List[Dict]:
    """
    Retrieves potentially relevant restaurants based on a simple keyword search
    in the structured data. Replace with more sophisticated methods later.
    """
    relevant_restaurants = []
    keywords = query.lower().split()
    for restaurant in data:
        text_to_search = (restaurant.get('name', '') + ' ' +
                          restaurant.get('cuisine', '') + ' ' +
                          restaurant.get('ambiance', '') + ' ' +
                          restaurant.get('features', '')).lower()
        print(text_to_search)
        if all(keyword in text_to_search for keyword in keywords):
            relevant_restaurants.append(restaurant)
    return relevant_restaurants[:top_n]

# --- Function to generate the LLM prompt for reasoning and ranking ---
def create_ranking_prompt(query: str, restaurants: List[Dict]) -> str:
    """Creates the prompt for the LLM to rank restaurants."""
    prompt = f"User query: {query}\n\n"
    prompt += "Here is information about some Riverside restaurants:\n\n"
    for i, restaurant in enumerate(restaurants):
        prompt += f"Restaurant {i+1}:\n"
        for key, value in restaurant.items():
            prompt += f"{key.title()}: {value}\n"
        prompt += "\n"

    prompt += f"Based on the user's query and the information provided above, identify the restaurants that best match ALL the criteria. Rank these restaurants from best to worst according to how well they satisfy the query. Explain your reasoning for each ranking, highlighting specific details from their descriptions. At the end, tell me how far away it is from UCR in miles\n"
    prompt += f"Put it in this format: Name, Rating(Reviews), Reasoning, Distance, each seperated by a line. Seperate each prediction by a semicolon"
    return prompt

# --- Function to call Azure OpenAI for ranking ---
def rank_restaurants(prompt: str, deployment_name: str = "YOUR_DEPLOYMENT_NAME") -> str:
    """Calls Azure OpenAI to get the ranked list of restaurants."""
    try:
        messages = [{"role": "user", "content": prompt}]  
        response = client.chat.completions.create(model=deployment, messages=messages, max_tokens=600, temperature = 0.1)
        return response.choices[0].message.content
    except:
        print(f"Error calling Azure OpenAI:")
        return ""

# --- Main function to handle user queries ---
def predict_best_restaurants(user_query: str, deployment_name: str = "YOUR_DEPLOYMENT_NAME"):
    """
    Takes a user query and returns the LLM's ranked list of best restaurants.
    """
    #relevant = retrieve_relevant_restaurants(user_query, restaurant_data)

   # if not relevant:
      #  return "No restaurants found matching your criteria."

    prompt = create_ranking_prompt(user_query, [])
    llm_response = rank_restaurants(prompt, deployment_name)

    return llm_response

if __name__ == "__main__":
    user_q = input("What type of dining experience are you looking for today: ")
    predictions = predict_best_restaurants(user_q)
    print(f"Predictions for '{user_q}':\n{predictions}")