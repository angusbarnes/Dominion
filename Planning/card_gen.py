import hashlib
import base64
import random
from typing import List
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont


def short_hash_case_insensitive(data):
    """
    Generate a 6-character case-insensitive alphanumeric hash.
    
    Parameters:
    - data: Any input (string, number, object that can be converted to a string)
    
    Returns:
    - A 6-character uppercase alphanumeric hash (Base36)
    """
    # Ensure data is a string and encode to bytes
    data_bytes = str(data).encode('utf-8')

    # Create a SHA-256 hash
    sha256_hash = hashlib.sha256(data_bytes).digest()

    # Convert hash to an integer
    hash_int = int.from_bytes(sha256_hash, 'big')

    # Convert to Base36 (case-insensitive alphanumeric)
    base36_hash = ''
    alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    
    # Extract 6 characters from Base36
    while hash_int and len(base36_hash) < 6:
        base36_hash = alphabet[hash_int % 36] + base36_hash
        hash_int //= 36

    # Pad with leading zeros if necessary
    return base36_hash.rjust(6, '0')


high_damage_dual_attack_threshold = 70
ability_base_chance = 0.04
extreme_health_ability_boost = 0.60

class Card:
    health: int
    primary_attack: int
    power_rating: float
    rarity: str = "Common"
    has_ability: bool = False
    secondary_attack: int = 0
    unique_card_id: str

    def __init__(self, health, primary_attack):
        self.health = health
        self.primary_attack = primary_attack

        self.power_rating = health + 1.2 * primary_attack

        self.rarity = self.categorize_rarity(self.power_rating)

        _random_state_backup = random.getstate()
        card_specific_seed = random.randint(1,3)
        random.seed(self.health * card_specific_seed)


        #TODO: Make parameters accessible to the card class
        if self.primary_attack >= high_damage_dual_attack_threshold:
            self.secondary_attack = int(round((att * random.uniform(0.25, 0.5))/10)*10)

            # Probability of an ability slot increases at extreme health values
        health_proximity = abs(self.health - 70) / (100 - 20)
        ability_chance = ability_base_chance + health_proximity * extreme_health_ability_boost
        self.has_ability = random.random() < ability_chance


        random.setstate(_random_state_backup)

        self.unique_card_id = short_hash_case_insensitive([self.health, self.primary_attack, card_specific_seed])

    def __str__(self):
        return f"{self.unique_card_id} [{self.power_rating}] {self.rarity}: Health: {self.health}, Att: {self.primary_attack}, {self.secondary_attack}, Ability: {self.has_ability}"

    def __repr__(self):
        return self.__str__()
    
    def __hash__(self):
        return self.unique_card_id

    @staticmethod
    def categorize_rarity(power_rating):

        if power_rating >= 200:
            return "Legendary"

        if power_rating >= 170:
            return "Ultra Rare"
        
        if power_rating >= 138:
            return "Rare"
        
        if power_rating >= 106:
            return "Uncommon"
        
        return "Common"
    
def generate_card_image(card, filename="card.png"):
    width, height = int(300 * 2.5), int(300* 3.5)
    bg_color = "white"
    
    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Fonts (use a basic font if PIL default fonts are unavailable)
    try:
        font = ImageFont.truetype("arial.ttf", 45)
    except:
        font = ImageFont.load_default()
    
    title_font = ImageFont.truetype("arial.ttf", 50) if font else font
    
    # Card border
    draw.rectangle([(10, 10), (width - 10, height - 10)], outline="black", width=10)

    draw.ellipse([(width - 80, 30), (width - 30, 80)], outline="black", width=4)

    draw.rectangle([(45, 90), (width - 45, 520)], outline="black", width=10)
    
    # Title
    draw.text((40, 30), f"Card ID: {card.unique_card_id}", fill="black", font=title_font)
    
    # Health
    draw.text((660, 30), f"{card.health}", fill="red", font=font)
    
    # Attack
    draw.text((40, 700), f"Primary Attack: {card.primary_attack}", fill="blue", font=font)
    if card.secondary_attack:
        draw.text((40, 800), f"Secondary Attack: {card.secondary_attack}", fill="blue", font=font)
    
        # Ability
    ability_text = "Yes" if card.has_ability else "No"
    draw.text((40, 600), f"Ability: {ability_text}", fill="green", font=font)
    # Power Rating
    #draw.text((40, 700), f"Power: {card.power_rating:.1f}", fill="black", font=font)
    
    # Rarity
    draw.text((40, 520), f"{card.rarity} Card", fill="gold", font=font)
    

    
    # Save image
    img.save(filename)
    print(f"Card image saved as {filename}")



def short_hash(data):
    """
    Generate a 6-character alphanumeric hash from arbitrary data.

    Parameters:
    - data: The input data (string, bytes, or any object that can be converted to a string)

    Returns:
    - A 6-character alphanumeric hash
    """
    # Ensure data is a string and encode to bytes
    data_bytes = str(data).encode('utf-8')

    # Create a SHA-256 hash
    sha256_hash = hashlib.sha256(data_bytes).digest()

    # Encode to base64 (URL-safe, but includes "-" and "_")
    base64_hash = base64.urlsafe_b64encode(sha256_hash).decode('utf-8')

    # Replace non-alphanumeric characters (just in case) and truncate to 6 characters
    alphanumeric_hash = ''.join(filter(str.isalnum, base64_hash))[:6]

    return alphanumeric_hash



def generate_stats(distribution="normal", mean=50, std_dev=15, num_samples=1000):
    """
    Generate random stats based on either a normal or logistic distribution.

    Parameters:
    - distribution: "normal" or "logistic"
    - mean: The mean (center) of the distribution
    - std_dev: The standard deviation (spread)
    - num_samples: Number of values to generate

    Returns:
    - List of generated values
    """
    if distribution == "normal":
        stats = np.random.normal(loc=mean, scale=std_dev, size=num_samples)
    elif distribution == "logistic":
        scale = std_dev / 1.813  # Approximate mapping of std_dev to logistic scale
        stats = np.random.logistic(loc=mean, scale=scale, size=num_samples)
    else:
        raise ValueError("Invalid distribution type. Choose 'normal' or 'logistic'.")

    return stats

def plot_distribution(stats, title="Stat Distribution"):
    """
    Plot a histogram of the generated stats.

    Parameters:
    - stats: List of values
    - title: Title of the histogram
    """
    vals, bins, bars = plt.hist(stats, bins=100, alpha=0.75, color="blue", edgecolor="black", density=True)
    plt.title(title)
    plt.xlabel("Value")
    plt.ylabel("Density")
    plt.grid()
    plt.show()

# Example Usage:
if __name__ == "__main__":

    count = {
        "Legendary": 0,
        "Common": 0,
        "Ultra Rare": 0,
        "Uncommon": 0,
        "Rare": 0
    }

    PACK_COUNT = 10
    best_card_found = None
    best_power = 0

    cards_made = 0
    abilities_made = 0
    ability_bins = {}
    ability_stats = []
    for i in range(PACK_COUNT):
        #stats = logistic_curve_stats(min_val=0, max_val=100, num_samples=200, k=8)
        # plot_distribution(stats, title="Logistic (Sigmoid) Curve Distribution")
        
        #Maybe use 30 for booster creation reasons?
        stats = generate_stats(distribution="normal", mean=50, std_dev=32, num_samples=28)
        stats = np.round(stats/10) * 10

        valid_cards: List[Card] = []

        for stat in stats:

            if stat < 20: continue
            cards_made += 1
            att = round(random.uniform(stat*0.3, stat)*0.8/10)*10

            card = Card(health=stat, primary_attack=att)

            if card.has_ability:
                abilities_made += 1
                ability_stats.append(stat)
                if stat in ability_bins:
                    ability_bins[stat] += 1
                else:
                    ability_bins[stat] = 1

            #print(f"Health: {stat}, Attack: {att}")
            valid_cards.append(card)

        #plot_distribution(stats, title=f"{distribution_type.capitalize()} Distribution")

        valid_cards.sort(key=lambda x: x.power_rating)

        # power_ratings = []
        # for stat in valid_stats:
        #     power_ratings.append(stat[0])

        
        # percentiles = np.percentile(power_ratings, np.arange(0, 101, 5))

        # # Print percentile ranges
        # for i in range(len(percentiles) - 1):
        #     print(f"{i * 5}-{(i + 1) * 5}%: {percentiles[i]:.2f} to {percentiles[i + 1]:.2f}")

        # plot_distribution(power_ratings, title=f"Power Distribution")



        print(valid_cards[0])

        count[valid_cards[0].rarity] += 1


        best_card = valid_cards[-1]

        if best_card.power_rating > best_power:
            best_power = best_card.power_rating
            best_card_found = best_card


        count[best_card.rarity] += 1

        pack_choices = valid_cards[1:-1]

        choices = random.sample(pack_choices, k=13)
        for choice in choices:
            print(choice)
            count[choice.rarity] += 1

        print(best_card)

    print(f"{abilities_made} Abilities / {cards_made} Cards [{abilities_made/cards_made * 100 :.2f}]")

    #plt.bar(np.array(list(ability_bins.keys())), np.array(list(ability_bins.values())))
    # plt.hist(ability_stats, bins=15)
    # plt.show()

    print(" ")
    print(count)
    print("============================")
    print(f"Total: {PACK_COUNT * 15}")
    print(f"Common: {count['Common']} [{(count['Common']/(PACK_COUNT * 15)) * 100:.2f}%] 1-in-{round(1/(count['Common']/(PACK_COUNT * 15.0)))}")
    print(f"Uncommon: {count['Uncommon']} [{(count['Uncommon']/(PACK_COUNT * 15)) * 100:.2f}%] 1-in-{round(1/(count['Uncommon']/(PACK_COUNT * 15.0)))}")
    print(f"Rare: {count['Rare']} [{(count['Rare']/(PACK_COUNT * 15)) * 100:.2f}%] 1-in-{round(1/(count['Rare']/(PACK_COUNT * 15)))}")
    print(f"Ultra Rare: {count['Ultra Rare']} [{(count['Ultra Rare']/(PACK_COUNT * 15)) * 100:.2f}%] 1-in-{round(1/(count['Ultra Rare']/(PACK_COUNT * 15.0)))}")
    print(f"Legendary: {count['Legendary']} [{(count['Legendary']/(PACK_COUNT * 15)) * 100:.2f}%] 1-in-{round(1/(count['Legendary']/(PACK_COUNT * 15.0)))}")
    print("")
    print(f"Best card: {best_card_found}")

        # Example card object
    card = Card(health=85, primary_attack=60)
    generate_card_image(card, "sample_card.png")
