#!/usr/bin/env python3
"""
Test script for document analysis endpoint
Tests the complete flow: upload -> analyze -> retrieve results
"""
import os
import sys
import requests
from pathlib import Path

# Add parent directory to path to import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
AUTH_TOKEN = os.getenv("AUTH_TOKEN", "")  # Set your JWT token here


def get_headers():
    """Get authentication headers"""
    if not AUTH_TOKEN:
        print("Error: AUTH_TOKEN environment variable not set")
        print("Please set it with: export AUTH_TOKEN='your-jwt-token'")
        sys.exit(1)

    return {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Content-Type": "application/json"
    }


def create_sample_text_file():
    """Create a sample text file for testing"""
    sample_text = """
    The industrious student embarked on a comprehensive analysis of photosynthesis.
    She examined the chloroplast structure meticulously, noting how chlorophyll
    molecules absorb light energy. The investigation revealed intricate biochemical
    pathways that convert carbon dioxide and water into glucose.

    Her hypothesis suggested that environmental factors significantly influence
    the rate of photosynthesis. Through systematic experimentation, she discovered
    that temperature, light intensity, and carbon dioxide concentration all play
    crucial roles in this fundamental biological process.

    The conclusion demonstrated exceptional understanding of cellular respiration
    and its relationship to photosynthesis. These interconnected processes maintain
    the delicate balance of our ecosystem, supporting life on Earth through the
    continuous exchange of oxygen and carbon dioxide.
    """

    filepath = "/tmp/test_analysis_sample.txt"
    with open(filepath, "w") as f:
        f.write(sample_text)

    return filepath


def test_analysis_flow():
    """Test the complete document analysis flow"""

    print("=" * 70)
    print("DOCUMENT ANALYSIS ENDPOINT TEST")
    print("=" * 70)
    print()

    # Step 1: Get list of students
    print("Step 1: Fetching students...")
    response = requests.get(
        f"{API_BASE_URL}/api/students",
        headers=get_headers()
    )

    if response.status_code != 200:
        print(f"Error fetching students: {response.status_code}")
        print(response.text)
        return

    students = response.json()
    if not students:
        print("No students found. Please create a student first.")
        return

    student = students[0]
    print(f"✓ Using student: {student['name']} (Grade {student['grade_level']})")
    print()

    # Step 2: Get existing documents for this student
    print("Step 2: Checking existing documents...")
    response = requests.get(
        f"{API_BASE_URL}/api/documents/students/{student['id']}/documents",
        headers=get_headers()
    )

    if response.status_code != 200:
        print(f"Error fetching documents: {response.status_code}")
        print(response.text)
        return

    documents = response.json()

    # Use first pending document if available, otherwise we'll need to upload
    document = None
    if documents:
        # Look for a pending or completed document
        for doc in documents:
            if doc['status'] in ['pending', 'completed']:
                document = doc
                break

    if not document:
        print("No suitable documents found.")
        print("Please upload a document first using the upload endpoint.")
        print("Or manually create one for testing.")
        return

    print(f"✓ Using document: {document['title']} (Status: {document['status']})")
    print()

    # Step 3: Analyze the document
    print("Step 3: Analyzing document...")
    print(f"POST {API_BASE_URL}/api/documents/{document['id']}/analyze")

    response = requests.post(
        f"{API_BASE_URL}/api/documents/{document['id']}/analyze",
        headers=get_headers()
    )

    if response.status_code != 200:
        print(f"✗ Analysis failed: {response.status_code}")
        print(response.text)
        return

    analysis = response.json()
    print("✓ Analysis completed successfully!")
    print()

    # Display results
    print("=" * 70)
    print("ANALYSIS RESULTS")
    print("=" * 70)
    print()

    stats = analysis['statistics']
    print(f"Student Grade Level: {analysis['student_grade_level']}")
    print()
    print("Statistics:")
    print(f"  Total Words:        {stats['total_words']}")
    print(f"  Unique Words:       {stats['unique_words']}")
    print(f"  Analyzed Words:     {stats['analyzed_words']}")
    print(f"  Unknown Words:      {stats['unknown_words']} ({stats['unknown_percentage']:.1%})")
    print(f"  Average Grade Level: {stats['average_grade_level']:.1f}" if stats['average_grade_level'] else "  Average Grade Level: N/A")
    print()

    print("Word Categories:")
    print(f"  Below Grade:  {stats['below_grade_count']}")
    print(f"  At Grade:     {stats['at_grade_count']}")
    print(f"  Above Grade:  {stats['above_grade_count']}")
    print()

    print("Grade Distribution:")
    dist = analysis['grade_distribution']
    for grade in range(6, 13):
        key = f"grade_{grade}"
        percentage = dist.get(key, 0.0)
        if percentage > 0:
            bar = "█" * int(percentage * 50)
            print(f"  Grade {grade:2d}: {percentage:5.1%} {bar}")
    print()

    # Display challenging words
    challenging = analysis.get('challenging_words', [])
    if challenging:
        print(f"Top Challenging Words ({len(challenging)}):")
        for i, word in enumerate(challenging[:10], 1):
            grade = word.get('grade_level', 'N/A')
            freq = word.get('frequency', 0)
            print(f"  {i:2d}. {word['word']:20s} (Grade {grade}, used {freq}x)")
        print()

    # Step 4: Retrieve analysis again using GET endpoint
    print("=" * 70)
    print("RETRIEVING SAVED ANALYSIS")
    print("=" * 70)
    print()

    print("Step 4: Fetching saved analysis...")
    print(f"GET {API_BASE_URL}/api/documents/{document['id']}/analysis")

    response = requests.get(
        f"{API_BASE_URL}/api/documents/{document['id']}/analysis",
        headers=get_headers()
    )

    if response.status_code != 200:
        print(f"✗ Failed to retrieve analysis: {response.status_code}")
        print(response.text)
        return

    retrieved_analysis = response.json()
    print("✓ Successfully retrieved saved analysis!")
    print()

    # Verify results match
    if retrieved_analysis['statistics']['total_words'] == stats['total_words']:
        print("✓ Saved analysis matches original analysis")
    else:
        print("✗ Warning: Saved analysis differs from original")
    print()

    # Step 5: Check document status
    print("Step 5: Verifying document status...")
    response = requests.get(
        f"{API_BASE_URL}/api/documents/{document['id']}",
        headers=get_headers()
    )

    if response.status_code == 200:
        updated_doc = response.json()
        print(f"✓ Document status: {updated_doc['status']}")
        if updated_doc['status'] == 'completed':
            print("✓ Document marked as completed")
        elif updated_doc['status'] == 'failed':
            print(f"✗ Document marked as failed: {updated_doc.get('error_message', 'Unknown error')}")
    print()

    print("=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    try:
        test_analysis_flow()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
