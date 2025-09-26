import re
import sys
import json
from docling.document_converter import DocumentConverter

def get_chapters(content, chapter_name=None):
    """
    Extracts chapters, words, definitions, and examples from a given text content.
    If chapter_name is specified, it only extracts data for that chapter efficiently.
    """
    # Efficiently handle the case for a single chapter
    if chapter_name:
        words_in_chapter = []
        current_word_info = None
        in_target_chapter = False
        for line in content.split('\n'):
            line = line.strip()
            if not line:
                continue

            if line.startswith('## ') and line[3:].isupper():
                current_chapter_title = line[3:]
                if in_target_chapter and current_chapter_title != chapter_name:
                    # We've hit the next chapter, so we can stop.
                    break
                if current_chapter_title == chapter_name:
                    in_target_chapter = True
                    current_word_info = None
            elif in_target_chapter:
                if re.search(r'\[\w+\]', line):
                    match = re.search(r'\[(\w+)\]', line)
                    if match:
                        word_type = match.group(1)
                        parts = re.split(r'\s*\[' + word_type + r'\]\s*', line, maxsplit=1)
                        word = parts[0].strip()
                        definition = parts[1].strip() if len(parts) > 1 else ""
                        current_word_info = {
                            "word": word,
                            "word_type": word_type,
                            "definition": definition,
                            "examples": []
                        }
                        words_in_chapter.append(current_word_info)
                elif current_word_info:
                    current_word_info["examples"].append(line)
        return words_in_chapter

    # Original logic to get all chapters
    chapters = {}
    current_chapter = None
    current_word_info = None
    for line in content.split('\n'):
        line = line.strip()
        if not line:
            continue
        if line.startswith('## ') and line[3:].isupper():
            current_chapter = line[3:]
            chapters[current_chapter] = []
            current_word_info = None
        elif current_chapter and re.search(r'\[\w+\]', line):
            match = re.search(r'\[(\w+)\]', line)
            if match:
                word_type = match.group(1)
                parts = re.split(r'\s*\[' + word_type + r'\]\s*', line, maxsplit=1)
                word = parts[0].strip()
                definition = parts[1].strip() if len(parts) > 1 else ""
                current_word_info = {
                    "word": word,
                    "word_type": word_type,
                    "definition": definition,
                    "examples": []
                }
                chapters[current_chapter].append(current_word_info)
        elif current_word_info:
            current_word_info["examples"].append(line)
    return chapters

def test_get_chapters():
    """
    Tests the get_chapters function with a sample paragraph.
    """
    content = """## EDUCATION

Scholarship [Noun] (an award of financial support for a student to pursue their higher education).

He won a scholarship at the age of 16 and was teaching physics at 19.

She won a scholarship to study law at Harvard University.

## CAREER

Admission [Noun] (the act of accepting or allowing someone to enter a place or organization).
"""
    # Test fetching all chapters
    all_chapters = get_chapters(content)
    expected_all = {
        "EDUCATION": [
            {
                "word": "Scholarship", "word_type": "Noun", "definition": "(an award of financial support for a student to pursue their higher education).",
                "examples": ["He won a scholarship at the age of 16 and was teaching physics at 19.", "She won a scholarship to study law at Harvard University."]
            }
        ],
        "CAREER": [
            {"word": "Admission", "word_type": "Noun", "definition": "(the act of accepting or allowing someone to enter a place or organization).", "examples": []}
        ]
    }
    assert all_chapters == expected_all, f"Expected {expected_all}, but got {all_chapters}"

    # Test fetching a specific chapter
    education_chapter = get_chapters(content, "EDUCATION")
    assert education_chapter == expected_all["EDUCATION"], f"Expected {expected_all['EDUCATION']}, but got {education_chapter}"
    
    # Test fetching a non-existent chapter
    non_existent_chapter = get_chapters(content, "HEALTH")
    assert non_existent_chapter == [], f"Expected [], but got {non_existent_chapter}"

    print("All tests passed!")

def main():
    """
    Main function to run tests and extract a specific chapter from the PDF.
    """
    # Run tests first
    test_get_chapters()

    # Then, process the PDF file
    if len(sys.argv) != 2:
        print("\nUsage: python extract_chapters.py <CHAPTER_NAME>")
        print("Example: python extract_chapters.py EDUCATION")
        sys.exit(1)
        
    chapter_name_arg = sys.argv[1]
    
    try:
        converter = DocumentConverter()
        result = converter.convert('vocab.pdf')
        content = result.document.export_to_markdown()

        chapter_data = get_chapters(content, chapter_name_arg)

        if chapter_data:
            with open(f"output_data.json", "w") as f:
                f.write(json.dumps(chapter_data, indent=4))
            print(f"\nData saved to {chapter_name_arg}_data.json")
        else:
            print(f"\nChapter '{chapter_name_arg}' not found or contains no data.")

    except FileNotFoundError:
        print("\nError: vocab.pdf not found. Please make sure the file is in the correct directory.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == '__main__':
    main()
