"""
Hybrid NLP Entity Extractor Engine
Extracts intelligence entities (PERSON, PHONE, VEHICLE, LOCATION, ORGANIZATION, DATE, MONEY)
using spaCy NLP models with an advanced rule-based, regex, and gazetteer recognizer.
"""

import re
from typing import Dict, List, Set, Any, Optional

class EntityExtractor:
    def __init__(self):
        self.nlp = None
        self._load_nlp_model()

        # Regular Expressions for High-Precision Pattern Extraction
        # Indian/Standard Phone Numbers: 10-digit mobile, +91 prefixes, formatted
        self.phone_pattern = re.compile(
            r'(?:(?:\+?91[\-\s]?)?[6-9]\d{9})|(?:(?:\+?\d{1,3}[\-\s]?)?\(?\d{2,4}\)?[\-\s]?\d{3,4}[\-\s]?\d{3,4})'
        )
        
        # Vehicle License Plates (Indian state formats: MH12AB1234, DL-04-C-9988, etc.)
        self.vehicle_pattern = re.compile(
            r'\b[A-Z]{2}[-\s]?[0-9]{1,2}[-\s]?[A-Z]{1,3}[-\s]?[0-9]{4}\b',
            re.IGNORECASE
        )
        
        # Currency Amounts (e.g., ₹ 45,000, Rs. 1,50,000, $50000, 25 Lakhs, 5 Crores, INR 85000)
        self.money_pattern = re.compile(
            r'(?:[₹$€£]|Rs\.?|INR|USD)\s*[\d,]+(?:\.\d{2})?(?:\s*(?:Lakhs?|Crores?|Millions?|k|cr|l))?|\b\d+(?:,\d+)*(?:\.\d{2})?\s*(?:INR|USD|EUR|GBP|Lakhs?|Crores?)\b',
            re.IGNORECASE
        )
        
        # Standard Dates / Timestamps (e.g. 15 August 2026, 2025-01-01, 12/05/2026)
        self.date_pattern = re.compile(
            r'\b(?:\d{1,2}(?:st|nd|rd|th)?[\s/-]+(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[\s/,-]+\d{2,4}|\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{2,4})\b',
            re.IGNORECASE
        )

        # Common First and Last Names for Gazetteer Fallback
        self.known_first_names = {
            "rahul", "amit", "vikram", "suresh", "karan", "devendra", "pooja", "rohan", "anil", "deepak",
            "manish", "sunil", "pankaj", "rajesh", "sanjay", "ajay", "vikas", "gaurav", "nitin", "sachin",
            "tarun", "arun", "mohit", "ashok", "vijay", "mukesh", "dinesh", "kailash", "mahesh", "ramesh",
            "praveen", "alok", "harish", "hemant", "jagdish", "lalit", "manoj", "naresh", "omkar", "pradeep",
            "ravi", "sandip", "tushar", "umesh", "vinod", "yogesh", "abhishek", "brijesh", "chetan", "dharmesh",
            "farhan", "giridhar", "himanshu", "irfan", "jitendra", "kapil", "lakshman", "mayur", "naveen", "parag",
            "rupesh", "sameer", "tanmay", "uday", "varun", "yash", "zameer", "aniket", "bharat", "chirag",
            "divyansh", "eshwar", "faizan", "gopal", "hardik", "imran", "jayesh", "kunal", "lokesh", "mandar",
            "neeraj", "pramod", "raghav", "siddharth", "tejas", "uttam", "vishal", "yuvraj", "zubair", "aakash"
        }

        self.known_last_names = {
            "sharma", "verma", "deshmukh", "malhotra", "singhania", "d'souza", "dsouza", "patel", "mehta", "kapoor",
            "kumar", "singh", "joshi", "kulkarni", "patil", "shinde", "pawar", "bhide", "chauhan", "rathore",
            "yadav", "pandey", "mishra", "tiwari", "gupta", "agarwal", "bansal", "bhatia", "chawla", "dhillon",
            "gill", "khurana", "sodhi", "reddy", "rao", "nair", "menon", "pillai", "iyer", "iyengar", "hegde",
            "shetty", "pai", "banerjee", "chatterjee", "mukherjee", "dutta", "ghosh", "sengupta", "bose", "das", "roy", "sen"
        }

        # Facility keywords for multi-word location capture
        self.facility_keywords = [
            "railway station", "container terminal", "industrial warehouse", "financial tower",
            "cargo gate", "fishing jetty", "regal plaza", "cargo terminal", "tech park",
            "safehouse", "transit depot", "tank farm", "cyber towers", "freight yard",
            "hideout villa", "farmhouse bunker", "apmc market", "diamond bourse", "dock",
            "harbor gate", "toll plaza", "airport", "railway", "station", "plaza", "warehouse", "depot"
        ]

        # Preloaded Known Cities & Hotspots
        self.known_locations = {
            "pune", "mumbai", "goa", "delhi", "bangalore", "ahmedabad", "hyderabad", "kutch", "panaji",
            "ratnagiri", "lonavala", "surat", "nagpur", "jaipur", "kolkata", "chennai", "thane",
            "panvel", "nashik", "kolhapur", "aurangabad", "solapur", "chandigarh", "indore", "bhopal",
            "lucknow", "varanasi", "nhava sheva", "bandra kurla", "connaught place", "koramangala",
            "electronic city", "calangute", "dharavi", "ghodbunder", "hinjewadi"
        }

        self.known_organizations = {
            "northside logistics syndicate", "northside logistics", "apex global financial ring", "apex global",
            "coastal freight & smuggling cell", "coastal freight", "silverline import export", "silverline import",
            "falcon security solutions", "falcon security", "metro transit & warehousing", "metro transit",
            "bayview luxury casino", "bayview luxury", "national cyber fintech", "national cyber",
            "customs", "port trust", "fiu", "interpol", "cyber cell", "diamond bourse"
        }

        self.stopwords = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "with", "near", "from",
            "by", "about", "into", "through", "during", "before", "after", "above", "below", "up", "down",
            "under", "over", "between", "out", "off", "then", "once", "here", "there", "when", "where",
            "why", "how", "all", "any", "both", "each", "few", "more", "most", "other", "some", "such",
            "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "can", "will", "just",
            "don", "should", "now", "met", "using", "was", "were", "is", "are", "had", "has", "have",
            "suspect", "vehicle", "phone", "transaction", "recorded", "contacted", "observed", "arrived"
        }

    def _load_nlp_model(self):
        """Attempts to load spaCy model, falls back cleanly if not installed."""
        try:
            import spacy
            try:
                self.nlp = spacy.load("en_core_web_sm")
            except Exception:
                try:
                    self.nlp = spacy.load("en_core_web_md")
                except Exception:
                    self.nlp = None
        except ImportError:
            self.nlp = None

    def extract_entities_from_text(self, text: str) -> Dict[str, List[str]]:
        """
        Extracts all target entity types from raw text using hybrid NLP + regex pipeline.
        Returns a dictionary mapping entity types to unique extracted strings.
        """
        if not text or not isinstance(text, str):
            return {
                "PERSON": [],
                "PHONE": [],
                "VEHICLE": [],
                "LOCATION": [],
                "ORGANIZATION": [],
                "DATE": [],
                "MONEY": []
            }

        extracted: Dict[str, Set[str]] = {
            "PERSON": set(),
            "PHONE": set(),
            "VEHICLE": set(),
            "LOCATION": set(),
            "ORGANIZATION": set(),
            "DATE": set(),
            "MONEY": set()
        }

        # 1. Regex Extraction for structured patterns
        # Phone Numbers
        for match in self.phone_pattern.finditer(text):
            p = match.group().strip()
            digits = re.sub(r'[^\d]', '', p)
            if len(digits) >= 8:
                extracted["PHONE"].add(p)

        # Vehicles
        for match in self.vehicle_pattern.finditer(text):
            extracted["VEHICLE"].add(match.group().strip().upper().replace(" ", "").replace("-", ""))

        # Money
        for match in self.money_pattern.finditer(text):
            extracted["MONEY"].add(match.group().strip())

        # Dates
        for match in self.date_pattern.finditer(text):
            extracted["DATE"].add(match.group().strip())

        # 2. spaCy NLP Pipeline (if available)
        if self.nlp:
            try:
                doc = self.nlp(text)
                for ent in doc.ents:
                    clean_text = ent.text.strip()
                    if len(clean_text) < 2:
                        continue

                    if ent.label_ == "PERSON":
                        if not any(char.isdigit() for char in clean_text) and len(clean_text.split()) <= 4:
                            extracted["PERSON"].add(clean_text.title())
                    elif ent.label_ in ["GPE", "LOC", "FAC"]:
                        extracted["LOCATION"].add(clean_text.title())
                    elif ent.label_ == "ORG":
                        extracted["ORGANIZATION"].add(clean_text.title())
                    elif ent.label_ == "DATE":
                        extracted["DATE"].add(clean_text)
                    elif ent.label_ == "MONEY":
                        extracted["MONEY"].add(clean_text)
            except Exception as e:
                print(f"[EntityExtractor] Warning during spaCy pass: {e}")

        # 3. Rule-based Gazetteers & Context Patterns fallback / reinforcement
        # Person Name Pattern: 2 or 3 capitalized words (e.g. "Rahul Sharma", "Amit Kumar")
        name_candidate_pattern = re.compile(r'\b[A-Z][a-z]{1,15}(?:\s+[A-Z][a-z]{1,15}){1,2}\b')
        for match in name_candidate_pattern.finditer(text):
            candidate = match.group().strip()
            words = candidate.lower().split()
            
            # Check if any word is a known stopword or month/day
            if any(w in self.stopwords for w in words):
                continue
            if any(w in self.known_locations for w in words):
                continue

            # If first word is known first name or second word is known last name
            if words[0] in self.known_first_names or (len(words) > 1 and words[-1] in self.known_last_names):
                extracted["PERSON"].add(candidate.title())
            elif len(words) == 2:
                # Plausible 2-word proper name
                extracted["PERSON"].add(candidate.title())

        # Check for single standalone known first names if they appear near action verbs like "met Amit", "contacted Amit"
        single_name_pattern = re.compile(r'\b(?:met|suspect|with|and|by|from|to)\s+([A-Z][a-z]{2,15})\b', re.IGNORECASE)
        for match in single_name_pattern.finditer(text):
            s_name = match.group(1).strip()
            if s_name.lower() in self.known_first_names and s_name.lower() not in self.stopwords:
                # Add standalone only if not already part of a multi-word name
                if not any(s_name.lower() in p.lower().split() for p in extracted["PERSON"]):
                    extracted["PERSON"].add(s_name.title())

        # Labeled headers in intelligence notes (e.g., PERSONS: Rahul, Amit)
        lines = text.split("\n")
        for line in lines:
            line_str = line.strip()
            
            if re.search(r'PERSONS?[:\-]', line_str, re.IGNORECASE):
                names_part = re.sub(r'PERSONS?[:\-]', '', line_str, flags=re.IGNORECASE)
                for part in re.split(r'[,;&]', names_part):
                    part_clean = part.strip()
                    if part_clean and len(part_clean) > 2 and not part_clean.lower().startswith("none"):
                        extracted["PERSON"].add(part_clean.title())

            if re.search(r'LOCATIONS?[:\-]', line_str, re.IGNORECASE):
                loc_part = re.sub(r'LOCATIONS?[:\-]', '', line_str, flags=re.IGNORECASE)
                for part in re.split(r'[,;&]', loc_part):
                    part_clean = part.strip()
                    if part_clean and len(part_clean) > 2:
                        extracted["LOCATION"].add(part_clean.title())

            if re.search(r'ORGANIZATIONS?[:\-]', line_str, re.IGNORECASE):
                org_part = re.sub(r'ORGANIZATIONS?[:\-]', '', line_str, flags=re.IGNORECASE)
                for part in re.split(r'[,;&]', org_part):
                    part_clean = part.strip()
                    if part_clean and len(part_clean) > 2:
                        extracted["ORGANIZATION"].add(part_clean.title())

        # Match compound locations like "Pune railway station", "Nhava Sheva container terminal"
        for loc in self.known_locations:
            # Check for loc + facility keyword
            for fac in self.facility_keywords:
                pattern = rf'\b{re.escape(loc)}\s+{re.escape(fac)}\b'
                m = re.search(pattern, text, re.IGNORECASE)
                if m:
                    extracted["LOCATION"].add(m.group().title())

            # Also check simple known city if compound wasn't already captured
            if not any(loc in l.lower() for l in extracted["LOCATION"]):
                if re.search(r'\b' + re.escape(loc) + r'\b', text, re.IGNORECASE):
                    extracted["LOCATION"].add(loc.title())

        # Match known organizations
        for org in self.known_organizations:
            if re.search(r'\b' + re.escape(org) + r'\b', text, re.IGNORECASE):
                extracted["ORGANIZATION"].add(org.title())

        # Clean up any overlapping sub-strings in locations (prefer longer specific names)
        raw_locs = sorted(list(extracted["LOCATION"]), key=len, reverse=True)
        final_locations = set()
        for loc in raw_locs:
            loc_clean = loc.title()
            # If this loc is a strict substring of an already added longer location, skip
            if not any(loc_clean != existing and loc_clean in existing for existing in final_locations):
                final_locations.add(loc_clean)

        return {
            "PERSON": sorted(list(extracted["PERSON"])),
            "PHONE": sorted(list(extracted["PHONE"])),
            "VEHICLE": sorted(list(extracted["VEHICLE"])),
            "LOCATION": sorted(list(final_locations)),
            "ORGANIZATION": sorted(list(extracted["ORGANIZATION"])),
            "DATE": sorted(list(extracted["DATE"])),
            "MONEY": sorted(list(extracted["MONEY"]))
        }

    def extract_summary_stats(self, text: str) -> Dict[str, Any]:
        """Returns entity counts and detailed extraction breakdown."""
        entities = self.extract_entities_from_text(text)
        total_count = sum(len(v) for v in entities.values())
        return {
            "total_entities_found": total_count,
            "breakdown": {k: len(v) for k, v in entities.items()},
            "entities": entities
        }
