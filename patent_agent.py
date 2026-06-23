from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from patent_tools import PatentSearchClient
import json

# Initialize the AI model
llm = ChatOllama(model="llama3.2:1b", temperature=0)
patent_client = PatentSearchClient()

def search_patents(query):
    """Search for patents by keyword."""
    try:
        results = patent_client.search_patents(query, limit=5)
        if "error" in results:
            return f"Error: {results['error']}"
        
        patents = results.get("patents", [])
        if not patents:
            return "No patents found for this query."
        
        output = "📊 SEARCH RESULTS:\n\n"
        for i, patent in enumerate(patents, 1):
            output += f"{i}. Patent: {patent.get('patent_number', 'N/A')}\n"
            output += f"   Title: {patent.get('patent_title', 'No title')}\n"
            output += f"   Date: {patent.get('patent_date', 'N/A')}\n"
            abstract = patent.get('patent_abstract', 'No abstract')
            output += f"   Abstract: {abstract[:150]}...\n\n"
        
        return output
    except Exception as e:
        return f"Error: {str(e)}"

def novelty_check(claim):
    """Check novelty of a claim."""
    try:
        results = patent_client.search_by_claim(claim, limit=3)
        if "error" in results:
            return f"Error: {results['error']}"
        
        patents = results.get("patents", [])
        if not patents:
            return "✅ No similar patents found. This claim appears NOVEL!"
        
        output = "🔍 NOVELTY ASSESSMENT:\n\n"
        output += f"Found {len(patents)} similar patents:\n\n"
        for i, patent in enumerate(patents, 1):
            output += f"{i}. {patent.get('patent_number', 'N/A')}\n"
            output += f"   Title: {patent.get('patent_title', 'No title')}\n"
            output += f"   Date: {patent.get('patent_date', 'N/A')}\n"
        
        output += "\n⚠️ These similar patents may affect novelty."
        output += "\n💡 Consider: How does your claim differ?"
        
        return output
    except Exception as e:
        return f"Error: {str(e)}"

def analyze_with_ai(user_input, search_results=None):
    """Use AI to analyze patent data."""
    messages = [
        SystemMessage(content="You are a Patent Research Assistant. Analyze patents professionally."),
        HumanMessage(content=f"User query: {user_input}\n\nData: {search_results}\n\nProvide a clear, helpful analysis.")
    ]
    response = llm.invoke(messages)
    return response.content

def main():
    print("=" * 70)
    print("🧠 PATENT RESEARCH AGENT (WORKING VERSION)")
    print("=" * 70)
    print("\nCommands:")
    print("  search <query>  - Search for patents")
    print("  novelty <claim> - Check novelty of a claim")
    print("  exit            - Quit the program")
    print("=" * 70)
    
    while True:
        user_input = input("\n🔍 Enter command: ")
        
        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("👋 Goodbye!")
            break
        
        # Handle search command
        if user_input.lower().startswith("search "):
            query = user_input[7:]  # Remove "search "
            print(f"\n📊 Searching for: {query}")
            results = search_patents(query)
            print(results)
            
            # Ask AI for analysis
            print("\n🤖 AI Analysis:")
            ai_response = analyze_with_ai(query, results)
            print(ai_response)
            
        # Handle novelty command
        elif user_input.lower().startswith("novelty "):
            claim = user_input[8:]  # Remove "novelty "
            print(f"\n🔍 Checking novelty for: {claim[:50]}...")
            results = novelty_check(claim)
            print(results)
            
            # Ask AI for deeper analysis
            print("\n🤖 AI Analysis:")
            ai_response = analyze_with_ai(f"Novelty assessment for: {claim}", results)
            print(ai_response)
            
        else:
            # Treat as general query
            print(f"\n🔍 Processing: {user_input}")
            results = search_patents(user_input)
            print(results)
            
            print("\n🤖 AI Analysis:")
            ai_response = analyze_with_ai(user_input, results)
            print(ai_response)

if __name__ == "__main__":
    main()