#!/usr/bin/env python3
"""
Quick test script for Windows installation without lxml
"""

def test_core_imports():
    """Test core package imports"""
    print("🔍 Testing Core Package Imports...")
    
    try:
        import PyQt6
        print("✅ PyQt6 imported successfully")
    except ImportError as e:
        print(f"❌ PyQt6 failed: {e}")
    
    try:
        import google.generativeai
        print("✅ Google Generative AI imported successfully")
    except ImportError as e:
        print(f"❌ Google Generative AI failed: {e}")
    
    try:
        import chromadb
        print("✅ ChromaDB imported successfully")
    except ImportError as e:
        print(f"❌ ChromaDB failed: {e}")
    
    try:
        import sentence_transformers
        print("✅ Sentence Transformers imported successfully")
    except ImportError as e:
        print(f"❌ Sentence Transformers failed: {e}")

def test_xml_alternatives():
    """Test XML processing alternatives (no lxml)"""
    print("\n🔍 Testing XML Processing Alternatives...")
    
    try:
        import html5lib
        print("✅ html5lib imported successfully")
    except ImportError as e:
        print(f"❌ html5lib failed: {e}")
    
    try:
        import defusedxml.ElementTree
        print("✅ defusedxml imported successfully")
    except ImportError as e:
        print(f"❌ defusedxml failed: {e}")
    
    try:
        import xml.etree.ElementTree
        print("✅ xml.etree (built-in) available")
    except ImportError as e:
        print(f"❌ xml.etree failed: {e}")
    
    try:
        import xmltodict
        print("✅ xmltodict imported successfully")
    except ImportError as e:
        print(f"❌ xmltodict failed: {e}")

def test_web_scraping():
    """Test web scraping capabilities"""
    print("\n🔍 Testing Web Scraping Capabilities...")
    
    try:
        import requests
        print("✅ requests imported successfully")
    except ImportError as e:
        print(f"❌ requests failed: {e}")
    
    try:
        import bs4
        print("✅ BeautifulSoup4 imported successfully")
    except ImportError as e:
        print(f"❌ BeautifulSoup4 failed: {e}")
    
    try:
        import trafilatura
        print("✅ trafilatura imported successfully")
    except ImportError as e:
        print(f"❌ trafilatura failed: {e}")

def test_document_processing():
    """Test document processing capabilities"""
    print("\n🔍 Testing Document Processing...")
    
    try:
        import PyPDF2
        print("✅ PyPDF2 imported successfully")
    except ImportError as e:
        print(f"❌ PyPDF2 failed: {e}")
    
    try:
        import docx
        print("✅ python-docx imported successfully")
    except ImportError as e:
        print(f"❌ python-docx failed: {e}")
    
    try:
        import openpyxl
        print("✅ openpyxl imported successfully")
    except ImportError as e:
        print(f"❌ openpyxl failed: {e}")

def main():
    """Main test function"""
    print("🧪 Windows Installation Test (No lxml)")
    print("=" * 50)
    
    test_core_imports()
    test_xml_alternatives()
    test_web_scraping()
    test_document_processing()
    
    print("\n📊 Test Summary:")
    print("If all tests show ✅, your installation is working correctly!")
    print("If you see ❌, install the missing packages individually.")
    print("\n💡 Remember: This installation avoids lxml compilation issues!")

if __name__ == "__main__":
    main()
