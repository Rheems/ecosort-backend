import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from education.models import Category, QuizQuestion
from marketplace.models import PricingReference

# ── PLASTIC ──
plastic, created = Category.objects.get_or_create(
    name='plastic',
    defaults={
        'description': 'Plastic waste includes bottles, containers and packaging materials that can be recycled.',
        'sorting_guide': '1. Rinse all plastic bottles and containers before sorting\n2. Flatten bottles to save space in your recycling bag\n3. Remove all caps and lids before sorting\n4. Separate plastic from other waste types\n5. Place in your designated recyclables bag',
        'tips': 'Avoid pure water sachets, styrofoam and plastic bags — contamination from these can cause recycling buyers to reject the entire batch.'
    }
)
if created:
    QuizQuestion.objects.create(category=plastic, question='What should you do to plastic bottles before sorting?', option_a='Crush them with your feet', option_b='Rinse and flatten them', option_c='Burn them', option_d='Leave them as they are', correct_answer='B')
    QuizQuestion.objects.create(category=plastic, question='Which should NOT be included in plastic recycling?', option_a='Water bottles', option_b='Pure water sachets', option_c='Plastic containers', option_d='Detergent bottles', correct_answer='B')
    QuizQuestion.objects.create(category=plastic, question='Why should you remove caps from plastic bottles?', option_a='To make them lighter', option_b='Caps are different plastic and must be sorted separately', option_c='To make them smell better', option_d='Caps are not recyclable', correct_answer='B')
    QuizQuestion.objects.create(category=plastic, question='Why should you flatten plastic bottles?', option_a='To make them easier to burn', option_b='To save space in your recycling bag', option_c='To remove the label', option_d='To clean them faster', correct_answer='B')
    QuizQuestion.objects.create(category=plastic, question='What happens if you mix styrofoam with plastic recycling?', option_a='Nothing happens', option_b='It makes the batch more valuable', option_c='It can cause the entire batch to be rejected', option_d='It helps the recycling process', correct_answer='C')
    print("✅ Plastic created")
else:
    print("⏭️ Plastic already exists, skipping")


# ── GLASS ──
glass, created = Category.objects.get_or_create(
    name='glass',
    defaults={
        'description': 'Glass waste includes bottles and jars that can be recycled. Safety is the top priority when handling glass waste.',
        'sorting_guide': '1. Only accept whole glass food and drink bottles\n2. Never crush or break glass intentionally\n3. If glass breaks accidentally, wrap it carefully in newspaper\n4. Place wrapped broken glass in a clearly labelled bag\n5. Verbally warn the collector about broken glass to prevent injury',
        'tips': 'Safety first — broken glass causes severe injuries. Always handle with care and warn collectors about any broken pieces.'
    }
)
if created:
    QuizQuestion.objects.create(category=glass, question='What should you NEVER do with glass waste?', option_a='Rinse it', option_b='Crush or break it intentionally', option_c='Store it separately', option_d='Label the bag', correct_answer='B')
    QuizQuestion.objects.create(category=glass, question='What should you do if glass breaks accidentally?', option_a='Leave it on the floor', option_b='Throw it in general waste', option_c='Wrap it in newspaper and label the bag', option_d='Crush it further to save space', correct_answer='C')
    QuizQuestion.objects.create(category=glass, question='Which glass items are accepted for recycling?', option_a='Broken window glass', option_b='Whole glass food and drink bottles', option_c='Light bulbs', option_d='Mirrors', correct_answer='B')
    QuizQuestion.objects.create(category=glass, question='Why must you warn the collector about broken glass?', option_a='To get more points', option_b='To prevent severe injury to the collector', option_c='Because it is a rule', option_d='To speed up collection', correct_answer='B')
    QuizQuestion.objects.create(category=glass, question='How should you store glass waste before collection?', option_a='Mixed with other recyclables', option_b='Crushed in a bag', option_c='Separately in a clearly labelled bag', option_d='In a plastic bag with food waste', correct_answer='C')
    print("✅ Glass created")
else:
    print("⏭️ Glass already exists, skipping")


# ── METAL ──
metal, created = Category.objects.get_or_create(
    name='metal',
    defaults={
        'description': 'Metal waste includes aluminium cans and tin or steel cans. Different metals require different handling to ensure safety and recycling quality.',
        'sorting_guide': '1. Separate aluminium cans from tin and steel cans\n2. Aluminium cans can be gently crushed to save space\n3. Do NOT crush tin or steel cans — they create dangerous sharp edges\n4. Never include aerosol cans in metal recycling\n5. Never include batteries — they are hazardous e-waste',
        'tips': 'Aerosol cans and batteries present extreme fire and explosion risks. Never include them in metal recycling.'
    }
)
if created:
    QuizQuestion.objects.create(category=metal, question='Which type of can can be gently crushed?', option_a='Tin cans', option_b='Steel cans', option_c='Aluminium cans', option_d='Aerosol cans', correct_answer='C')
    QuizQuestion.objects.create(category=metal, question='Why should you NOT crush tin or steel cans?', option_a='They take up too much space', option_b='They create dangerous sharp edges', option_c='They are too heavy', option_d='They cannot be recycled', correct_answer='B')
    QuizQuestion.objects.create(category=metal, question='Which should NEVER be included in metal recycling?', option_a='Aluminium cans', option_b='Steel food cans', option_c='Aerosol cans', option_d='Tin cans', correct_answer='C')
    QuizQuestion.objects.create(category=metal, question='Why are batteries dangerous in metal recycling?', option_a='They are too heavy', option_b='They present fire and explosion risks', option_c='They cannot be crushed', option_d='They are too small', correct_answer='B')
    QuizQuestion.objects.create(category=metal, question='Where should batteries be disposed of?', option_a='In the metal recycling bag', option_b='In general waste', option_c='In e-waste collection — they are hazardous', option_d='In the organic waste bag', correct_answer='C')
    print("✅ Metal created")
else:
    print("⏭️ Metal already exists, skipping")


# ── PAPER ──
paper, created = Category.objects.get_or_create(
    name='paper',
    defaults={
        'description': 'Paper and cardboard waste must be kept dry at all times. Moisture is the leading cause of paper batch rejection by recycling buyers.',
        'sorting_guide': '1. Ensure all paper and cardboard is completely dry before sorting\n2. Keep paper elevated off the ground to prevent moisture absorption\n3. Do not include wax-coated juice cartons or Tetra Paks\n4. Do not include greasy food wrappers like pizza boxes\n5. Flatten cardboard boxes to save space',
        'tips': 'Moisture is the number one enemy of paper recycling. Even slightly wet paper can cause an entire batch to be rejected.'
    }
)
if created:
    QuizQuestion.objects.create(category=paper, question='What is the most important rule for paper recycling?', option_a='Paper must be colourful', option_b='Paper must be dry', option_c='Paper must be folded', option_d='Paper must be white', correct_answer='B')
    QuizQuestion.objects.create(category=paper, question='Why should paper be kept elevated off the ground?', option_a='To make it easier to collect', option_b='To prevent moisture absorption', option_c='To save space', option_d='To keep it clean from dust', correct_answer='B')
    QuizQuestion.objects.create(category=paper, question='Which is NOT accepted in paper recycling?', option_a='Newspapers', option_b='Cardboard boxes', option_c='Greasy pizza boxes', option_d='Office paper', correct_answer='C')
    QuizQuestion.objects.create(category=paper, question='What happens if wet paper is included in recycling?', option_a='Nothing happens', option_b='It makes the batch more valuable', option_c='The entire batch can be rejected', option_d='It helps other paper dry faster', correct_answer='C')
    QuizQuestion.objects.create(category=paper, question='Which is also NOT accepted in paper recycling?', option_a='Brown cardboard', option_b='Wax-coated juice cartons', option_c='Newspapers', option_d='Magazines', correct_answer='B')
    print("✅ Paper created")
else:
    print("⏭️ Paper already exists, skipping")


# ── ORGANIC ──
organic, created = Category.objects.get_or_create(
    name='organic',
    defaults={
        'description': 'Organic waste includes food scraps and biodegradable materials. Proper separation protects the value of recyclables and supports composting.',
        'sorting_guide': '1. Use the Three-Bag Separation System: Recyclables, Organic, General waste\n2. Never mix food scraps with recyclable materials\n3. Food residue ruins recyclable batches — always keep separate\n4. For composting, use a repurposed bucket with holes for airflow\n5. Note: Organic waste pickups are not yet available — compost at home for now',
        'tips': 'The Three-Bag Separation System is the foundation of Ecosort. Keeping organic waste separate protects the value of every recyclable batch.'
    }
)
if created:
    QuizQuestion.objects.create(category=organic, question='What is the Three-Bag Separation System?', option_a='Plastic, Glass, Metal', option_b='Recyclables, Organic, General waste', option_c='Wet, Dry, Hazardous', option_d='Paper, Plastic, Food', correct_answer='B')
    QuizQuestion.objects.create(category=organic, question='Why must food scraps be kept separate from recyclables?', option_a='Food makes recyclables heavier', option_b='Food residue ruins recyclable batches', option_c='Food attracts collectors', option_d='Food makes recycling easier', correct_answer='B')
    QuizQuestion.objects.create(category=organic, question='What household item can be used for home composting?', option_a='A plastic bottle', option_b='A repurposed bucket with holes for airflow', option_c='A sealed metal tin', option_d='A glass jar', correct_answer='B')
    QuizQuestion.objects.create(category=organic, question='Are organic waste pickups currently available on Ecosort?', option_a='Yes every day', option_b='Yes on weekends only', option_c='No compost at home for now', option_d='Yes for premium users', correct_answer='C')
    QuizQuestion.objects.create(category=organic, question='What happens if food residue is mixed with recyclables?', option_a='Nothing happens', option_b='It increases the value of the batch', option_c='It ruins the recyclable batch', option_d='It helps the composting process', correct_answer='C')
    print("✅ Organic created")
else:
    print("⏭️ Organic already exists, skipping")


# ── EWASTE ──
ewaste, created = Category.objects.get_or_create(
    name='ewaste',
    defaults={
        'description': 'Electronic waste includes old phones, cables, batteries and all electrical devices. E-waste contains toxic materials that must never be burned.',
        'sorting_guide': '1. NEVER BURN E-WASTE — this is the most critical rule\n2. Identify e-waste: old phones, cables, batteries, chargers, laptops\n3. Store e-waste separately from all other waste types\n4. Text the keyword EWASTE to our WhatsApp bot to find local drop-off points\n5. Never throw e-waste in general waste bins',
        'tips': 'Burning e-waste releases highly toxic lead, mercury and arsenic into the air — causing serious health risks to your family and community.'
    }
)
if created:
    QuizQuestion.objects.create(category=ewaste, question='What is the most critical rule for e-waste?', option_a='Crush it to save space', option_b='Never burn it', option_c='Mix it with metal recycling', option_d='Wash it before disposal', correct_answer='B')
    QuizQuestion.objects.create(category=ewaste, question='Which of these is considered e-waste?', option_a='Glass bottles', option_b='Cardboard boxes', option_c='Old phones and cables', option_d='Plastic containers', correct_answer='C')
    QuizQuestion.objects.create(category=ewaste, question='What toxic chemicals are released when e-waste is burned?', option_a='Carbon dioxide only', option_b='Lead mercury and arsenic', option_c='Oxygen and nitrogen', option_d='Water vapour', correct_answer='B')
    QuizQuestion.objects.create(category=ewaste, question='How can you find a safe e-waste drop-off point?', option_a='Call the helpline', option_b='Visit the office', option_c='Text EWASTE to the WhatsApp bot', option_d='Leave it at the roadside', correct_answer='C')
    QuizQuestion.objects.create(category=ewaste, question='Where should e-waste be stored before drop-off?', option_a='Mixed with general waste', option_b='With metal recycling', option_c='Separately from all other waste', option_d='In the organic waste bag', correct_answer='C')
    print("✅ E-waste created")
else:
    print("⏭️ E-waste already exists, skipping")


# ── PRICING REFERENCE (Updated Lagos Market 2026) ──
PricingReference.objects.update_or_create(
    material_type='plastic',
    defaults={
        'min_price_per_kg': 240,
        'max_price_per_kg': 350,
        'suggested_price_per_kg': 300,
        'source': 'Lagos Market Clusters 2026 — Mushin, Ojota, Alaba'
    }
)
PricingReference.objects.update_or_create(
    material_type='paper',
    defaults={
        'min_price_per_kg': 60,
        'max_price_per_kg': 100,
        'suggested_price_per_kg': 80,
        'source': 'Lagos Market Clusters 2026 — Mushin, Ojota, Alaba'
    }
)
PricingReference.objects.update_or_create(
    material_type='glass',
    defaults={
        'min_price_per_kg': 20,
        'max_price_per_kg': 40,
        'suggested_price_per_kg': 30,
        'source': 'Lagos Market 2026'
    }
)
PricingReference.objects.update_or_create(
    material_type='metal',
    defaults={
        'min_price_per_kg': 180,
        'max_price_per_kg': 850,
        'suggested_price_per_kg': 450,
        'source': 'Lagos Market Clusters 2026 — Mushin, Ojota, Alaba'
    }
)
PricingReference.objects.update_or_create(
    material_type='organic',
    defaults={
        'min_price_per_kg': 10,
        'max_price_per_kg': 20,
        'suggested_price_per_kg': 15,
        'source': 'Lagos Market 2026'
    }
)
PricingReference.objects.update_or_create(
    material_type='ewaste',
    defaults={
        'min_price_per_kg': 200,
        'max_price_per_kg': 1500,
        'suggested_price_per_kg': 700,
        'source': 'Lagos Market Clusters 2026 — Mushin, Ojota, Alaba'
    }
)
print("✅ Pricing reference data updated!")

print("\n🌿 Database population complete!")