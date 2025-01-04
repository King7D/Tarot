from flask import Flask, render_template, request
import json
import random
from collections import Counter

app = Flask(__name__)

# Load Tarot cards data on startup
with open('tarot_cards.json', 'r', encoding='utf-8') as f:
    tarot_cards = json.load(f)

def generate_card_analysis(drawn_cards):
    """
    Utility function that gathers keywords, elements, numerology, astrology, etc.
    Returns a dictionary of counts and relevant lists for further analysis.
    """
    data = {
        'all_keywords': [],
        'elements': [],
        'numerology': [],
        'astrology': [],
        'major_arcana': [],
        'suits': []
    }
    for card in drawn_cards:
        data['all_keywords'].extend(card.get('keywords', []))
        if card.get('element'):
            data['elements'].append(card['element'])
        if card.get('numerology'):
            data['numerology'].append(card['numerology'])
        if card.get('astrology'):
            data['astrology'].append(card['astrology'])
        if card['arcana'] == "Major":
            data['major_arcana'].append(card)
        else:
            # Try to find suit if "of" is in the card name.
            name_parts = card['name'].split()
            if "of" in name_parts:
                of_index = name_parts.index("of")
                if of_index + 1 < len(name_parts):
                    data['suits'].append(name_parts[of_index + 1])
    return data

def synergy_analysis(drawn_cards):
    """
    Provides synergy/combination notes among the drawn cards.
    """
    if len(drawn_cards) < 2:
        # No synergy with single card
        return ""

    synergy_text = "<h5>Card Combinations & Synergy:</h5>"
    found_any_synergy = False
    
    for i in range(len(drawn_cards)):
        for j in range(i + 1, len(drawn_cards)):
            c1 = drawn_cards[i]
            c2 = drawn_cards[j]
            
            synergy_msgs = []
            
            # If both are Major Arcana
            if c1['arcana'] == "Major" and c2['arcana'] == "Major":
                synergy_msgs.append(
                    "Both are Major Arcana, indicating powerful, life-altering influences."
                )
            
            # Same element
            if c1.get('element') and c2.get('element') and c1['element'] == c2['element']:
                synergy_msgs.append(
                    f"Both share the element <strong>{c1['element']}</strong>, intensifying that elemental energy."
                )
            
            # Same suit (for Minor Arcana)
            if "of" in c1['name'] and "of" in c2['name']:
                name_parts_1 = c1['name'].split()
                name_parts_2 = c2['name'].split()
                if "of" in name_parts_1 and "of" in name_parts_2:
                    suit_1 = name_parts_1[name_parts_1.index("of") + 1]
                    suit_2 = name_parts_2[name_parts_2.index("of") + 1]
                    if suit_1 == suit_2:
                        synergy_msgs.append(
                            f"Both are from the suit of <strong>{suit_1}</strong>, reinforcing shared themes."
                        )
            
            # Same numerology
            if c1.get('numerology') and c2.get('numerology'):
                if c1['numerology'] == c2['numerology']:
                    synergy_msgs.append(
                        f"Both resonate with the number <strong>{c1['numerology']}</strong>, amplifying that numerical influence."
                    )
            
            # Overlapping astrology
            if c1.get('astrology') and c2.get('astrology'):
                c1_astros = set([x.strip() for x in c1['astrology'].split(',')])
                c2_astros = set([x.strip() for x in c2['astrology'].split(',')])
                shared_astros = c1_astros.intersection(c2_astros)
                if shared_astros:
                    synergy_msgs.append(
                        f"They share astrological influence(s): <strong>{', '.join(shared_astros)}</strong>."
                    )
            
            if synergy_msgs:
                found_any_synergy = True
                synergy_text += (
                    f"<p><strong>{c1['name']}</strong> &amp; <strong>{c2['name']}</strong>: "
                    + " ".join(synergy_msgs)
                    + "</p>"
                )
    
    if not found_any_synergy:
        synergy_text += "<p>No strong synergy overlaps were detected among these cards.</p>"
    
    return synergy_text

def numerology_special_notes(numerology_counts):
    """
    Returns special interpretation for certain numbers (1, 5, 10).
    """
    notes = []
    if "1" in numerology_counts:
        notes.append(
            "<p><strong>Numerology #1 (Aces or The Magician)</strong>: "
            "Symbolizes new beginnings, fresh starts, or the spark of creativity. "
            "Be prepared for pioneering energy and personal initiative.</p>"
        )
    if "5" in numerology_counts:
        notes.append(
            "<p><strong>Numerology #5</strong>: Associated with change, challenges, and transitions. "
            "This number often invites you to adapt, push through conflicts, and embrace growth "
            "through instability.</p>"
        )
    if "10" in numerology_counts:
        notes.append(
            "<p><strong>Numerology #10</strong>: Represents completion, culmination of a cycle, and transition "
            "into a new phase. Reflect on what is ending and be open to the fresh possibilities that follow.</p>"
        )
    return "".join(notes)

def generate_overall_interpretation(drawn_cards, spread_type="Custom Spread"):
    """
    Generates an overall interpretation for single-card, three-card, five-card, and ten-card draws
    (and any custom number of cards in between).
    """
    interpretation = ""
    data = generate_card_analysis(drawn_cards)

    # Count occurrences
    keyword_counts = Counter(data['all_keywords'])
    repeated_keywords = [k for k, v in keyword_counts.items() if v > 1]
    element_counts = Counter(data['elements'])
    numerology_counts = Counter(data['numerology'])
    astrology_counts = Counter(data['astrology'])
    suit_counts = Counter(data['suits'])

    # ---- 1) Single-Card Draw ----
    if spread_type == "Single-Card Draw":
        card = drawn_cards[0]
        orientation_text = "Upright" if card['orientation'] == 'upright' else "Reversed"
        interpretation += (
            f"<h4>{spread_type}</h4>"
            f"<p>You drew <strong>{card['name']}</strong> ({orientation_text}).</p>"
        )
        # Provide a little info about element/numerology/astrology
        if card.get('element'):
            interpretation += f"<p><strong>Element:</strong> {card['element']}</p>"
        if card.get('numerology'):
            interpretation += f"<p><strong>Number:</strong> {card['numerology']}</p>"
        if card.get('astrology'):
            interpretation += f"<p><strong>Astrology:</strong> {card['astrology']}</p>"
        
        # If it’s a major arcana
        if card['arcana'] == "Major":
            interpretation += (
                "<p>This is a Major Arcana card, indicating a powerful theme or life lesson. "
                "Expect significant energies surrounding this card’s meaning.</p>"
            )
        
        # Special note if that single card is numerology 1, 5, or 10
        if card.get('numerology') in ["1", "5", "10"]:
            # Just reuse our helper
            single_note_counts = {card['numerology']: 1}
            interpretation += "<h5>Special Numerology Note:</h5>"
            interpretation += numerology_special_notes(single_note_counts)
        
        interpretation += (
            "<p>A single-card draw offers a concise message or insight. "
            "Reflect on how this card’s energy resonates with your question or intention.</p>"
        )
        return interpretation

    # ---- 2) Three-Card Spread ----
    elif spread_type == "Three-Card Spread":
        positions = ['Past', 'Present', 'Future']
        interpretation += f"<h4>{spread_type}</h4>"
        for pos, card in zip(positions, drawn_cards):
            orientation_text = "Upright" if card['orientation'] == 'upright' else "Reversed"
            desc = card['upright'] if card['orientation'] == 'upright' else card['reversed']
            interpretation += f"<p><strong>{pos} ({orientation_text}):</strong> {desc}</p>"
        
        interpretation += standard_analysis(drawn_cards, data)
        return interpretation

    # ---- 3) Five-Card Spread ----
    elif spread_type == "Five-Card Spread":
        # Example positions (you can rename or remove positions as you see fit):
        positions = ['Situation', 'Challenge', 'Guidance', 'Focus', 'Potential']
        interpretation += f"<h4>{spread_type}</h4>"
        for pos, card in zip(positions, drawn_cards):
            orientation_text = "Upright" if card['orientation'] == 'upright' else "Reversed"
            desc = card['upright'] if card['orientation'] == 'upright' else card['reversed']
            interpretation += f"<p><strong>{pos} ({orientation_text}):</strong> {desc}</p>"
        
        interpretation += standard_analysis(drawn_cards, data)
        return interpretation

    # ---- 4) Celtic Cross Spread (10 cards) ----
    elif spread_type == "Celtic Cross Spread":
        # A typical Celtic Cross might label positions as:
        positions = [
            "Present Position",
            "Immediate Challenge",
            "Distant Past",
            "Recent Past",
            "Goal or Aspiration",
            "Future Influence",
            "You as You See Yourself",
            "Outside Influences",
            "Hopes and Fears",
            "Outcome"
        ]
        interpretation += f"<h4>{spread_type}</h4>"
        for pos, card in zip(positions, drawn_cards):
            orientation_text = "Upright" if card['orientation'] == 'upright' else "Reversed"
            desc = card['upright'] if card['orientation'] == 'upright' else card['reversed']
            interpretation += f"<p><strong>{pos} ({orientation_text}):</strong> {desc}</p>"
        
        interpretation += standard_analysis(drawn_cards, data)
        return interpretation

    # ---- Catch-all for other draws (2 cards, 4 cards, 6-9 cards, etc.) ----
    else:
        interpretation += f"<h4>{spread_type}</h4>"
        for i, card in enumerate(drawn_cards, start=1):
            orientation_text = "Upright" if card['orientation'] == 'upright' else "Reversed"
            desc = card['upright'] if card['orientation'] == 'upright' else card['reversed']
            interpretation += f"<p><strong>Card {i} ({orientation_text}):</strong> {desc}</p>"
        
        interpretation += standard_analysis(drawn_cards, data)
        return interpretation


def standard_analysis(drawn_cards, data):
    """
    A helper function that produces a standard analysis block, used by multi-card spreads
    (3, 5, 10, or custom). This block includes repeated keywords, elemental balance, 
    numerology, astrology, synergy, etc.
    """
    interpretation = ""

    keyword_counts = Counter(data['all_keywords'])
    repeated_keywords = [k for k, v in keyword_counts.items() if v > 1]
    element_counts = Counter(data['elements'])
    numerology_counts = Counter(data['numerology'])
    astrology_counts = Counter(data['astrology'])
    suit_counts = Counter(data['suits'])
    
    # Shared keywords
    if repeated_keywords:
        interpretation += "<h5>Key Themes (Shared Keywords):</h5><ul>"
        for keyword in repeated_keywords:
            interpretation += f"<li>{keyword}</li>"
        interpretation += "</ul>"
        interpretation += "<p>These keywords appear in multiple cards, indicating heightened significance.</p>"
    else:
        interpretation += "<p>No repeated keywords—each card brings its own distinct energy.</p>"

    # Elemental balance
    if element_counts:
        interpretation += "<h5>Elemental Balance:</h5><ul>"
        for elem, count in element_counts.items():
            interpretation += f"<li>{elem}: {count} card(s)</li>"
        interpretation += "</ul>"
        interpretation += "<p>Shows the distribution of Fire, Water, Air, Earth energies in your reading.</p>"

    # Numerology 
    if numerology_counts:
        interpretation += "<h5>Numerological Insights:</h5><ul>"
        for num, count in numerology_counts.items():
            interpretation += f"<li>Number {num}: {count} card(s)</li>"
        interpretation += "</ul>"

        # Insert special notes for 1, 5, and 10
        special_notes = numerology_special_notes(numerology_counts)
        if special_notes:
            interpretation += "<h5>Special Numerology Notes:</h5>"
            interpretation += special_notes

    # Astrology
    if astrology_counts:
        interpretation += "<h5>Astrological Influences:</h5><ul>"
        for astro, count in astrology_counts.items():
            interpretation += f"<li>{astro}: {count} card(s)</li>"
        interpretation += "</ul>"
        interpretation += "<p>Astrological aspects can further clarify the energies at play.</p>"

    # Major Arcana presence
    major_arcanas = data['major_arcana']
    if major_arcanas:
        interpretation += (
            "<h5>Major Arcana Notes:</h5>"
            "<p>Major Arcana cards point to significant life themes or transformative moments. "
            "Pay close attention to these powerful energies.</p>"
        )

    # Dominant suit in Minor Arcana
    if data['suits']:
        suit_counts = Counter(data['suits'])
        dominant_suit, count = suit_counts.most_common(1)[0]
        interpretation += (
            f"<h5>Dominant Suit:</h5><p>The suit of <strong>{dominant_suit}</strong> appears most frequently, "
            "indicating a focus on related aspects (e.g., Cups = emotions, Pentacles = material matters, "
            "Swords = thoughts/communication, Wands = creativity/passion).</p>"
        )

    # Synergy
    synergy_text = synergy_analysis(drawn_cards)
    if synergy_text:
        interpretation += synergy_text

    # Final
    interpretation += (
        "<p>Overall, reflect on these recurring themes, elemental energies, numbers, suits, and card synergies "
        "to gain deeper insight into your question or situation.</p>"
    )

    return interpretation


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/draw', methods=['POST'])
def draw():
    try:
        num_cards = int(request.form.get('num_cards', 3))
        if num_cards < 1 or num_cards > 10:
            num_cards = 3  # default fallback
    except ValueError:
        num_cards = 3

    # Ensure not to sample more cards than available
    if num_cards > len(tarot_cards):
        num_cards = len(tarot_cards)

    # Draw random unique cards
    drawn_cards = random.sample(tarot_cards, num_cards)
    
    # Assign orientation to each card
    for card in drawn_cards:
        card['orientation'] = random.choice(['upright', 'reversed'])

    # Determine spread type based on number of cards
    if num_cards == 1:
        spread_type = "Single-Card Draw"
    elif num_cards == 3:
        spread_type = "Three-Card Spread"
    elif num_cards == 5:
        spread_type = "Five-Card Spread"
    elif num_cards == 10:
        spread_type = "Celtic Cross Spread"
    else:
        spread_type = "Custom Spread"

    # Generate overall interpretation
    overall = generate_overall_interpretation(drawn_cards, spread_type)

    return render_template('result.html', cards=drawn_cards, overall_interpretation=overall, spread_type=spread_type)

if __name__ == '__main__':
    app.run(debug=True)
