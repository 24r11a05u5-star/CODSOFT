import re
import random

class CosmicTravelBot:
    def __init__(self):
      
        self.rules = {
            r'.*\b(hello|hi|hey|greetings|howdy)\b.*': [
                "Greetings, Earthling! I am Nebula, your Cosmic Travel Guide. Where would you like to blast off to today?",
                "Hello! Ready to leave the stratosphere? Ask me about our planetary vacation packages!"
            ],
            r'.*\b(mars|red planet)\b.*': [
                "Ah, Mars! The rusted jewel. Pack light, the gravity is only 38% of Earth's. It takes about 7 months to get there.",
                "Mars is a classic choice. Don't forget to visit Olympus Mons, the tallest volcano in the solar system!"
            ],
            r'.*\b(moon|luna)\b.*': [
                "The Moon is perfect for a weekend getaway. Just a quick 3-day trip. Watch your step, the dust is clingy!",
                "A lunar vacation! We have great deals on Apollo landing site tours."
            ],
            r'.*\b(cost|price|expensive|money|cheap|ticket)\b.*': [
                "Space travel isn't cheap, but we offer zero-gravity financing! A standard Moon ticket starts at $2.5 million.",
                "Prices vary based on the alignment of the planets, but expect to empty a few earthly bank accounts."
            ],
            r'.*\b(safe|safety|danger|die|scary)\b.*': [
                "Safety is our 4th highest priority! Our ships only have a microscopic chance of spontaneous decompression.",
                "You will be fine! Probably. Just don't take your helmet off outside."
            ],
            r'.*\b(bye|goodbye|quit|exit|cya)\b.*': [
                "Signing off! May your stars always align. Goodbye!",
                "Over and out. Catch you on the dark side of the moon!"
            ]
        }

        # Fallback responses if the user says something the bot doesn't understand
        self.fallback_responses = [
            "My planetary sensors didn't catch that. Could you rephrase?",
            "Interesting... but let's talk about space travel! Want to hear about Mars or the Moon?",
            "That's above my clearance level. Ask me about booking a flight instead."
        ]

    def process_input(self, user_input):
        # NLP Step 1: Normalization (converting text to lowercase to make matching easier)
        user_input = user_input.lower()

        # NLP Step 2: Intent Recognition via Pattern Matching
        for pattern, responses in self.rules.items():
            if re.match(pattern, user_input):
                return random.choice(responses)

        # NLP Step 3: Fallback handling
        return random.choice(self.fallback_responses)

    def start_conversation(self):
        print("Nebula System Online. Type 'quit' to exit the console.")
        print("-" * 60)
        
        while True:
            user_input = input("You: ")
            
            # Prevent crashing on empty inputs
            if not user_input.strip():
                continue

            # Get the bot's response
            response = self.process_input(user_input)
            print(f"Nebula: {response}")

            # Break the loop if the user wants to leave
            if re.match(r'.*\b(bye|goodbye|quit|exit)\b.*', user_input.lower()):
                break

# Standard Python execution block
if __name__ == "__main__":
    bot = CosmicTravelBot()
    bot.start_conversation()