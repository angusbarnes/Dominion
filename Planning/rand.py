import hashlib
import base64
import random
import numpy as np
import matplotlib.pyplot as plt

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


def logistic_curve_stats(min_val=0, max_val=100, num_samples=1000, k=10):
    """
    Generate values following a logistic (sigmoid) curve.

    Parameters:
    - min_val: Minimum possible value
    - max_val: Maximum possible value
    - num_samples: Number of samples to generate
    - k: Steepness of the logistic curve (higher = more extreme values)

    Returns:
    - Array of generated values
    """
    # Generate uniform random numbers in range [-6, 6] to cover most of the sigmoid curve
    x = np.range()

    # Apply the sigmoid function
    sigmoid_values = 1 / (1 + np.exp(-k * x))

    # Scale to desired range
    scaled_values = min_val + (max_val - min_val) * sigmoid_values

    return scaled_values


ratios = [
    (15, 10),
    (2, 1),
    (2, 1),
    (3, 1),
    (3, 1),
]

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

def format_card(stats):
    return f"{short_hash_case_insensitive(stats)} [{stats[0]}] {categorize_rarity(stats[0])}: Health: {stats[1]}, Att: {stats[2]}"

# Example Usage:
if __name__ == "__main__":
    distribution_type = "normal"  # Change to "logistic" for logistic distribution
    
    # stats = logistic_curve_stats(min_val=0, max_val=100, num_samples=200, k=8)
    # plot_distribution(stats, title="Logistic (Sigmoid) Curve Distribution")
    
    #Maybe use 30 for booster creation reasons?
    stats = generate_stats(distribution=distribution_type, mean=50, std_dev=30, num_samples=25)
    stats = np.round(stats/10) * 10

    valid_stats = []
    for stat in stats:
        health_modifier, attack_modifier = random.choice(ratios)
        if stat < 20: continue
        att = round(random.uniform(stat*0.3, stat)*0.8/10)*10
        #print(f"Health: {round(stat*(health_modifier/(health_modifier+attack_modifier))/10)*10}, Attack: {round(stat*(attack_modifier/(health_modifier+attack_modifier))/10)*10}")
        #print(f"Health: {stat}, Attack: {att}")
        valid_stats.append((stat+att*1.2, stat, att, random.randint(1,3)))

    #plot_distribution(stats, title=f"{distribution_type.capitalize()} Distribution")

    valid_stats.sort(key=lambda x: x[0])

    # power_ratings = []
    # for stat in valid_stats:
    #     power_ratings.append(stat[0])

    
    # percentiles = np.percentile(power_ratings, np.arange(0, 101, 5))

    # # Print percentile ranges
    # for i in range(len(percentiles) - 1):
    #     print(f"{i * 5}-{(i + 1) * 5}%: {percentiles[i]:.2f} to {percentiles[i + 1]:.2f}")

    # plot_distribution(power_ratings, title=f"Power Distribution")

    print(format_card(valid_stats[0]))
    best_card = valid_stats[-1]
    
    pack_choices = valid_stats[1:-1]

    choices = random.sample(pack_choices, k=13)
    for choice in choices:
        print(format_card(choice))

    print(format_card(best_card))