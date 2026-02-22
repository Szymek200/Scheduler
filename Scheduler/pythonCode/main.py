# Ask the user for their name
name = input("What's your name? ")
age = int(input("How old are you? "))

# A simple logic check
if age >= 18:
    print(f"Hello, {name}! You're an adult.")
else:
    print(f"Hey {name}, you've still got {18 - age} years until adulthood!")