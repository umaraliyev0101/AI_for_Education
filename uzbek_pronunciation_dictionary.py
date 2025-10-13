#!/usr/bin/env python3
"""
Uzbek Pronunciation Dictionary
Comprehensive pronunciation guide for Uzbek educational terms
"""

import json
import os
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum

class UzbekPhonemeType(Enum):
    """Types of Uzbek phonemes"""
    VOWEL = "vowel"
    CONSONANT = "consonant"
    DIPHTHONG = "diphthong"

@dataclass
class UzbekPhoneme:
    """Uzbek phoneme with pronunciation information"""

    symbol: str
    cyrillic: str
    latin: str
    type: UzbekPhonemeType
    description: str
    examples: List[str]
    difficulty_level: str  # beginner, intermediate, advanced

@dataclass
class UzbekPronunciationEntry:
    """Pronunciation entry for a word"""

    word: str
    cyrillic: str
    latin: str
    phonetic_transcription: str  # IPA
    syllables: List[str]
    stress_pattern: str
    pronunciation_guide: str
    common_mispronunciations: List[str]
    difficulty_level: str
    category: str
    audio_examples: List[str]  # file paths to audio examples
    metadata: Dict[str, Any]

class UzbekPronunciationDictionary:
    """
    Comprehensive pronunciation dictionary for Uzbek educational terms
    """

    def __init__(self, dictionary_file: str = "uzbek_pronunciation_dictionary.json"):
        """Initialize the pronunciation dictionary"""

        self.dictionary_file = dictionary_file
        self.entries: Dict[str, UzbekPronunciationEntry] = {}

        # Load phoneme inventory
        self.phonemes = self._create_phoneme_inventory()

        # Load existing dictionary if available
        self.load_dictionary()

    def _create_phoneme_inventory(self) -> Dict[str, UzbekPhoneme]:
        """Create comprehensive Uzbek phoneme inventory"""

        phonemes = {}

        # Vowels
        vowels = [
            ("a", "а", "a", "Open front unrounded vowel", ["maktab", "qalam"], "beginner"),
            ("e", "е", "e", "Close-mid front unrounded vowel", ["men", "sen"], "beginner"),
            ("i", "и", "i", "Close front unrounded vowel", ["kitob", "qiziq"], "beginner"),
            ("o", "о", "o", "Close-mid back rounded vowel", ["o'qish", "bolalar"], "beginner"),
            ("u", "у", "u", "Close back rounded vowel", ["uy", "qush"], "beginner"),
            ("o'", "ў", "oʻ", "Close-mid back unrounded vowel", ["o'qituvchi", "o'quvchi"], "intermediate"),
            ("u'", "ў", "uʼ", "Close back unrounded vowel (rare)", ["quloq"], "advanced"),
        ]

        for symbol, cyrillic, latin, desc, examples, difficulty in vowels:
            phonemes[symbol] = UzbekPhoneme(
                symbol=symbol,
                cyrillic=cyrillic,
                latin=latin,
                type=UzbekPhonemeType.VOWEL,
                description=desc,
                examples=examples,
                difficulty_level=difficulty
            )

        # Consonants
        consonants = [
            ("b", "б", "b", "Voiced bilabial plosive", ["kitob", "bolalar"], "beginner"),
            ("p", "п", "p", "Voiceless bilabial plosive", ["pensiya", "pul"], "beginner"),
            ("d", "д", "d", "Voiced alveolar plosive", ["dars", "do'st"], "beginner"),
            ("t", "т", "t", "Voiceless alveolar plosive", ["maktab", "til"], "beginner"),
            ("g", "г", "g", "Voiced velar plosive", ["guruh", "gal"], "beginner"),
            ("k", "к", "k", "Voiceless velar plosive", ["kitob", "qalam"], "beginner"),
            ("q", "қ", "q", "Voiceless uvular plosive", ["qizil", "qush"], "intermediate"),
            ("v", "в", "v", "Voiced labiodental fricative", ["vazifa", "viloyat"], "beginner"),
            ("f", "ф", "f", "Voiceless labiodental fricative", ["fan", "fizika"], "beginner"),
            ("z", "з", "z", "Voiced alveolar fricative", ["zavod", "zamon"], "beginner"),
            ("s", "с", "s", "Voiceless alveolar fricative", ["sinf", "soat"], "beginner"),
            ("j", "ж", "j", "Voiced postalveolar fricative", ["jurnal", "jinoyat"], "intermediate"),
            ("sh", "ш", "sh", "Voiceless postalveolar fricative", ["shahar", "ish"], "beginner"),
            ("ch", "ч", "ch", "Voiceless postalveolar affricate", ["chiroq", "choy"], "beginner"),
            ("ng", "нг", "ng", "Velar nasal", ["rang", "singan"], "intermediate"),
            ("l", "л", "l", "Alveolar lateral approximant", ["maktab", "qalam"], "beginner"),
            ("m", "м", "m", "Bilabial nasal", ["maktab", "matematika"], "beginner"),
            ("n", "н", "n", "Alveolar nasal", ["nima", "non"], "beginner"),
            ("r", "р", "r", "Alveolar trill", ["raqam", "rangi"], "beginner"),
            ("h", "ҳ", "h", "Voiceless glottal fricative", ["halqa", "hayot"], "intermediate"),
            ("y", "й", "y", "Palatal approximant", ["yozish", "yangi"], "beginner"),
            ("'", "'", "'", "Glottal stop (hamza)", ["o'qish", "o'quvchi"], "intermediate"),
        ]

        for symbol, cyrillic, latin, desc, examples, difficulty in consonants:
            phonemes[symbol] = UzbekPhoneme(
                symbol=symbol,
                cyrillic=cyrillic,
                latin=latin,
                type=UzbekPhonemeType.CONSONANT,
                description=desc,
                examples=examples,
                difficulty_level=difficulty
            )

        return phonemes

    def add_educational_term(self, word: str, cyrillic: str, phonetic: str,
                           category: str, difficulty: str = "intermediate",
                           pronunciation_guide: str = "", common_mistakes: Optional[List[str]] = None) -> UzbekPronunciationEntry:
        """
        Add an educational term to the dictionary

        Args:
            word: Word in Latin script
            cyrillic: Word in Cyrillic script
            phonetic: IPA phonetic transcription
            category: Educational category
            difficulty: Difficulty level
            pronunciation_guide: Pronunciation instructions
            common_mistakes: Common mispronunciations

        Returns:
            PronunciationEntry object
        """

        if common_mistakes is None:
            common_mistakes = []

        # Analyze syllables and stress
        syllables, stress_pattern = self._analyze_syllables(word)

        # Generate pronunciation guide if not provided
        if not pronunciation_guide:
            pronunciation_guide = self._generate_pronunciation_guide(word, phonetic)

        entry = UzbekPronunciationEntry(
            word=word,
            cyrillic=cyrillic,
            latin=word,  # Assuming input is already Latin
            phonetic_transcription=phonetic,
            syllables=syllables,
            stress_pattern=stress_pattern,
            pronunciation_guide=pronunciation_guide,
            common_mispronunciations=common_mistakes,
            difficulty_level=difficulty,
            category=category,
            audio_examples=[],  # Will be populated later
            metadata={
                "added_date": "2025-01-13",
                "verified": False,
                "usage_frequency": "educational"
            }
        )

        self.entries[word.lower()] = entry
        return entry

    def _analyze_syllables(self, word: str) -> Tuple[List[str], str]:
        """Analyze word syllables and stress pattern"""

        # Simple syllable analysis (can be improved with linguistic rules)
        vowels = "aeiouo'uʼ"
        syllables = []
        current_syllable = ""

        for char in word.lower():
            current_syllable += char
            if char in vowels and len(current_syllable) > 1:
                syllables.append(current_syllable)
                current_syllable = ""

        if current_syllable:
            syllables.append(current_syllable)

        # Simple stress pattern (stress on penultimate syllable for Uzbek)
        stress_pattern = "0" * len(syllables)
        if len(syllables) > 1:
            stress_position = len(syllables) - 2  # Penultimate
            stress_pattern = stress_pattern[:stress_position] + "1" + stress_pattern[stress_position+1:]

        return syllables, stress_pattern

    def _generate_pronunciation_guide(self, word: str, phonetic: str) -> str:
        """Generate pronunciation guide from word and phonetic transcription"""

        guide_parts = []

        # Basic pronunciation notes
        if "q" in word:
            guide_parts.append("q is pronounced from the back of throat")
        if "o'" in word or "u'" in word:
            guide_parts.append("oʻ/uʼ are pronounced without lip rounding")
        if "h" in word:
            guide_parts.append("h is a strong throat sound")
        if "'" in word:
            guide_parts.append("' represents a brief pause/glottal stop")

        if not guide_parts:
            guide_parts.append("Pronounce clearly with equal emphasis on each syllable")

        return ". ".join(guide_parts)

    def load_educational_terms(self):
        """Load comprehensive list of educational terms"""

        educational_terms = [
            # Basic Education
            ("maktab", "maktab", "'mak.tɑb", "school", "education", "beginner"),
            ("o'qituvchi", "o'qituvchi", "o'.qi.tuʋ.tʃi", "teacher", "education", "beginner"),
            ("o'quvchi", "o'quvchi", "o'.quʋ.tʃi", "student", "education", "beginner"),
            ("dars", "dars", "dɑrs", "lesson", "education", "beginner"),
            ("sinf", "sinf", "sinf", "class", "education", "beginner"),
            ("kitob", "kitob", "ki.'tob", "book", "education", "beginner"),
            ("daftar", "daftar", "dɑf.'tɑr", "notebook", "education", "beginner"),
            ("qalam", "qalam", "qɑ.'lɑm", "pencil", "education", "beginner"),
            ("ruchka", "ruchka", "rutʃ.'kɑ", "pen", "education", "beginner"),
            ("doska", "doska", "dos.'kɑ", "blackboard", "education", "beginner"),

            # Subjects
            ("matematika", "matematika", "mɑ.te.mɑ.'ti.kɑ", "mathematics", "subject", "intermediate"),
            ("fizika", "fizika", "fi.'zi.kɑ", "physics", "subject", "intermediate"),
            ("kimyo", "kimyo", "kim.'jo", "chemistry", "subject", "intermediate"),
            ("biologiya", "biologiya", "bi.o.lo.'gi.jɑ", "biology", "subject", "intermediate"),
            ("tarix", "tarix", "tɑ.'rix", "history", "subject", "intermediate"),
            ("geografiya", "geografiya", "ge.o.grɑ.'fi.jɑ", "geography", "subject", "intermediate"),
            ("adabiyot", "adabiyot", "ɑ.dɑ.bi.'jot", "literature", "subject", "intermediate"),
            ("ona tili", "ona tili", "o.'nɑ ti.'li", "native language", "subject", "beginner"),
            ("ingliz tili", "ingliz tili", "in.'gliz ti.'li", "English language", "subject", "beginner"),

            # Learning Actions
            ("o'qish", "o'qish", "o'.qish", "reading", "action", "beginner"),
            ("yozish", "yozish", "jo.'zish", "writing", "action", "beginner"),
            ("o'rganish", "o'rganish", "or.'gɑ.nish", "learning", "action", "beginner"),
            ("tushunish", "tushunish", "tu.shu.'nish", "understanding", "action", "beginner"),
            ("eslash", "eslash", "es.'lɑsh", "remembering", "action", "beginner"),
            ("takrorlash", "takrorlash", "tɑk.ro.'rɑsh", "repeating", "action", "intermediate"),

            # Educational Concepts
            ("savol", "savol", "sɑ.'vol", "question", "concept", "beginner"),
            ("javob", "javob", "dʒɑ.'vob", "answer", "concept", "beginner"),
            ("vazifa", "vazifa", "vɑ.zi.'fɑ", "task", "concept", "beginner"),
            ("baholash", "baholash", "bɑ.ho.'lɑsh", "assessment", "concept", "intermediate"),
            ("imtihon", "imtihon", "im.ti.'hon", "exam", "concept", "intermediate"),
            ("diplom", "diplom", "di.'plom", "diploma", "concept", "intermediate"),

            # Numbers and Counting
            ("raqam", "raqam", "rɑ.'qɑm", "number", "math", "beginner"),
            ("hisoblash", "hisoblash", "hi.sob.'lɑsh", "calculating", "math", "intermediate"),
            ("qo'shish", "qo'shish", "qo'shish", "addition", "math", "beginner"),
            ("ayirish", "ayirish", "ɑ.'jirish", "subtraction", "math", "beginner"),
            ("ko'paytirish", "ko'paytirish", "kop.'pɑj.tirish", "multiplication", "math", "intermediate"),
            ("bo'lish", "bo'lish", "bo.'lish", "division", "math", "intermediate"),

            # Science Terms
            ("tajriba", "tajriba", "tɑdʒ.ri.'bɑ", "experiment", "science", "intermediate"),
            ("kashfiyot", "kashfiyot", "kɑsh.fi.'jot", "discovery", "science", "advanced"),
            ("tadqiqot", "tadqiqot", "tɑd.qi.'qot", "research", "science", "advanced"),
            ("nazariya", "nazariya", "nɑ.zɑ.ri.'jɑ", "theory", "science", "intermediate"),
            ("qonun", "qonun", "qo.'nun", "law", "science", "intermediate"),
        ]

        for term in educational_terms:
            word, cyrillic, phonetic, category, category_type, difficulty = term
            self.add_educational_term(
                word=word,
                cyrillic=cyrillic,
                phonetic=phonetic,
                category=f"{category_type}_{category}",
                difficulty=difficulty
            )

    def search_entries(self, query: str, category: Optional[str] = None,
                      difficulty: Optional[str] = None) -> List[UzbekPronunciationEntry]:
        """
        Search dictionary entries

        Args:
            query: Search term
            category: Filter by category
            difficulty: Filter by difficulty

        Returns:
            List of matching entries
        """

        results = []
        query_lower = query.lower()

        for entry in self.entries.values():
            # Text search
            if query_lower not in entry.word.lower() and query_lower not in entry.category.lower():
                continue

            # Category filter
            if category and category.lower() not in entry.category.lower():
                continue

            # Difficulty filter
            if difficulty and entry.difficulty_level != difficulty:
                continue

            results.append(entry)

        return results

    def get_phoneme_info(self, phoneme: str) -> Optional[UzbekPhoneme]:
        """Get information about a specific phoneme"""

        return self.phonemes.get(phoneme.lower())

    def save_dictionary(self):
        """Save dictionary to JSON file"""

        # Convert entries to dictionaries
        data = {
            "metadata": {
                "version": "1.0",
                "created_date": "2025-01-13",
                "total_entries": len(self.entries),
                "description": "Uzbek Pronunciation Dictionary for Educational Terms"
            },
            "phonemes": {k: {**asdict(v), "type": v.type.value} for k, v in self.phonemes.items()},
            "entries": {}
        }

        for word, entry in self.entries.items():
            data["entries"][word] = asdict(entry)

        with open(self.dictionary_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"💾 Saved {len(self.entries)} entries to {self.dictionary_file}")

    def load_dictionary(self):
        """Load dictionary from JSON file"""

        if not os.path.exists(self.dictionary_file):
            print(f"📖 Dictionary file {self.dictionary_file} not found, starting fresh")
            return

        try:
            with open(self.dictionary_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Load phonemes
            for symbol, phoneme_data in data.get("phonemes", {}).items():
                phoneme_data["type"] = UzbekPhonemeType(phoneme_data["type"])
                self.phonemes[symbol] = UzbekPhoneme(**phoneme_data)

            # Load entries
            for word, entry_data in data.get("entries", {}).items():
                self.entries[word] = UzbekPronunciationEntry(**entry_data)

            print(f"📖 Loaded {len(self.entries)} entries from {self.dictionary_file}")

        except Exception as e:
            print(f"❌ Error loading dictionary: {e}")

    def generate_pronunciation_report(self, category: Optional[str] = None) -> str:
        """Generate a pronunciation difficulty report"""

        entries = list(self.entries.values())
        if category:
            entries = [e for e in entries if category.lower() in e.category.lower()]

        if not entries:
            return "No entries found for the specified criteria."

        # Statistics
        total_entries = len(entries)
        difficulty_counts = {}
        category_counts = {}

        for entry in entries:
            difficulty_counts[entry.difficulty_level] = difficulty_counts.get(entry.difficulty_level, 0) + 1
            category_counts[entry.category] = category_counts.get(entry.category, 0) + 1

        report = f"""
UZBEK PRONUNCIATION DICTIONARY REPORT
{'='*40}

Total Entries: {total_entries}

Difficulty Distribution:
"""

        for difficulty, count in sorted(difficulty_counts.items()):
            percentage = (count / total_entries) * 100
            report += f"  {difficulty.capitalize()}: {count} ({percentage:.1f}%)\n"

        report += "\nCategory Distribution:\n"
        for category_name, count in sorted(category_counts.items()):
            percentage = (count / total_entries) * 100
            report += f"  {category_name}: {count} ({percentage:.1f}%)\n"

        report += "\nSample Entries:\n"
        for i, entry in enumerate(entries[:5]):
            report += f"  {i+1}. {entry.word} ({entry.phonetic_transcription}) - {entry.category}\n"

        return report

def create_uzbek_pronunciation_dictionary():
    """Create and populate the Uzbek pronunciation dictionary"""

    print("📖 UZBEK PRONUNCIATION DICTIONARY")
    print("=" * 40)

    # Create dictionary
    dictionary = UzbekPronunciationDictionary()

    # Load educational terms
    print("Loading educational terms...")
    dictionary.load_educational_terms()

    # Save dictionary
    dictionary.save_dictionary()

    # Generate report
    report = dictionary.generate_pronunciation_report()
    print(report)

    # Demonstrate search
    print("\n🔍 SEARCH DEMONSTRATION")
    print("-" * 25)

    # Search for math terms
    math_terms = dictionary.search_entries("math", category="subject")
    print(f"Found {len(math_terms)} math-related terms:")
    for term in math_terms[:3]:
        print(f"  {term.word}: {term.phonetic_transcription}")

    # Search for difficult phonemes
    print(f"\nPhoneme 'q' info: {dictionary.get_phoneme_info('q')}")

    return dictionary

if __name__ == "__main__":
    create_uzbek_pronunciation_dictionary()
