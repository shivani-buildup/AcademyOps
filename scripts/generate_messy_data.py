import csv
import random
import string

def generate_messy_data(output_path: str = "data/messy_leads.csv", num_rows: int = 250):
    first_names = ["John", "Jane", "Alice", "Bob", "michael", "sArAh", "David", "emma", "Chris", "olivia"]
    last_names = ["Smith", "Doe", "Johnson", "Brown", "williams", "jones", "Garcia", "miller", "Davis", "rodriguez"]
    sources = ["Facebook", "FB", "Instagram", "insta", "IG", "Google", "Website", "referral", ""]
    
    with open(output_path, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Phone", "Source", "Notes"])
        
        seen_phones = set()
        
        for i in range(num_rows):
            # 5% chance of missing name
            if random.random() < 0.05:
                name = ""
            else:
                fname = random.choice(first_names)
                lname = random.choice(last_names)
                # 20% chance of bad casing or whitespace
                if random.random() < 0.2:
                    name = f"  {fname.lower()} {lname.upper()}  "
                else:
                    name = f"{fname} {lname}"
            
            # 10% chance of missing phone
            if random.random() < 0.10:
                phone = ""
            # 15% chance of duplicate phone within batch
            elif seen_phones and random.random() < 0.15:
                phone = random.choice(list(seen_phones))
            else:
                # generate a random phone
                phone = f"555-{random.randint(1000, 9999)}"
                # 5% chance of bad phone format (letters)
                if random.random() < 0.05:
                    phone += random.choice(string.ascii_letters)
                
                if phone:
                    seen_phones.add(phone)
                    
            source = random.choice(sources)
            notes = f"Auto-generated note {i}" if random.random() > 0.5 else ""
            
            writer.writerow([name, phone, source, notes])
            
    print(f"Generated {num_rows} messy rows at {output_path}")

if __name__ == "__main__":
    generate_messy_data()
