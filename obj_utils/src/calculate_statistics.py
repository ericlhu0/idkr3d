from collections import defaultdict
import statistics

def analyze_categories(data_string):
    # Split the string into pairs of object and error
    pairs = data_string.strip().split()
    
    # Create dictionary to store errors by category
    categories = defaultdict(list)
    
    # Parse data and organize by category
    for i in range(0, len(pairs), 2):
        obj_name = pairs[i]
        error_val = float(pairs[i + 1])
        
        # Extract category from object name (everything before the number)
        category = ''.join(c for c in obj_name if not c.isdigit()).replace('.obj', '')
        categories[category].append(error_val)
    
    # Calculate statistics for each category
    print("Category Statistics:")
    print("-" * 50)
    all_errors = []
    
    for category, errors in sorted(categories.items()):
        all_errors.extend(errors)
        mean = statistics.mean(errors)
        median = statistics.median(errors)
        std_dev = statistics.stdev(errors) if len(errors) > 1 else 0
        min_val = min(errors)
        max_val = max(errors)

        if "pitcher" in category.lower():
            category = "Watering Pitcher"
        elif "mug" in category.lower():
            category = "Mug"
        elif "can" in category.lower():
            category = "Can"
        print(f"\n{category.upper()} (n={len(errors)}):")
        print(f"  Mean:   {mean:.4f}")
        print(f"  Median: {median:.4f}")
        print(f"  StdDev: {std_dev:.4f}")
        print(f"  Min:    {min_val:.4f}")
        print(f"  Max:    {max_val:.4f}")
    
    # Calculate overall statistics
    print("\n" + "=" * 50)
    print("OVERALL STATISTICS:")
    print(f"Total samples: {len(all_errors)}")
    print(f"Overall mean:   {statistics.mean(all_errors):.4f}")
    print(f"Overall median: {statistics.median(all_errors):.4f}")
    print(f"Overall StdDev: {statistics.stdev(all_errors):.4f}")
    print(f"Overall min:    {min(all_errors):.4f}")
    print(f"Overall max:    {max(all_errors):.4f}")

# Your data string
input_file = 'baseline_sdfs.txt'
with open(input_file, 'r') as output_file:
    data = output_file.read()


# Run the analysis
print(input_file)
analyze_categories(data)
