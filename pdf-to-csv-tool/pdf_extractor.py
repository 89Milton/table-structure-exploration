import os
import PyPDF2
import pandas as pd
from typing import List, Dict, Optional, Tuple
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
import tempfile
import re
from datetime import datetime

class PDFExtractor:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    def extract_text(self, use_ocr: bool = False) -> Tuple[str, List[Dict[str, str]]]:
        """
        Extract text from the PDF file.
        
        Args:
            use_ocr (bool): If True, uses OCR to extract text from images.
                           If False, tries to extract text directly.
        """
        if use_ocr:
            text = self._extract_text_with_ocr()
            return text, []  # OCR doesn't extract hyperlinks
        else:
            return self._extract_text_directly()

    def _extract_text_directly(self) -> Tuple[str, List[Dict[str, str]]]:
        """Try to extract text directly from the PDF."""
        text = ""
        hyperlinks = []
        try:
            with open(self.pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num, page in enumerate(pdf_reader.pages):
                    text += page.extract_text()
                    
                    # Extract hyperlinks if available
                    if '/Annots' in page:
                        for annot in page['/Annots']:
                            annotation = annot.get_object()
                            if annotation.get('/Subtype') == '/Link' and '/A' in annotation:
                                if '/URI' in annotation['/A']:
                                    url = annotation['/A']['/URI']
                                    # Get the text near the link if possible
                                    if '/Rect' in annotation:
                                        rect = annotation['/Rect']
                                        # Extract text near the link's position
                                        link_text = ""
                                        try:
                                            # Get text from the same page
                                            page_text = page.extract_text()
                                            # Simple approximation of link position in text
                                            link_text = page_text[max(0, int(rect[1])-100):min(len(page_text), int(rect[1])+100)]
                                        except:
                                            pass
                                        
                                        # Store link with its context
                                        hyperlinks.append({
                                            'url': url,
                                            'text': link_text,
                                            'page': page_num + 1
                                        })
            
            # If we got very little text, it might be a scanned document
            if len(text.strip()) < 100:
                print("Warning: Very little text extracted. The PDF might be scanned. Trying OCR...")
                return self._extract_text_with_ocr(), []
            
            return text, hyperlinks
        except Exception as e:
            print(f"Error extracting text directly: {str(e)}")
            print("Trying OCR as fallback...")
            return self._extract_text_with_ocr(), []

    def _extract_text_with_ocr(self) -> str:
        """Extract text using OCR."""
        try:
            # Convert PDF to images
            images = convert_from_path(self.pdf_path)
            text = ""
            
            # Process each page
            for i, image in enumerate(images):
                # Save image temporarily
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                    image.save(temp_file.name)
                    # Extract text using OCR
                    page_text = pytesseract.image_to_string(Image.open(temp_file.name))
                    text += page_text + "\n"
                os.unlink(temp_file.name)  # Clean up temp file
            
            return text
        except Exception as e:
            raise Exception(f"OCR processing failed: {str(e)}")

    def extract_to_csv(self, output_path: str, data_processor=None, use_ocr: bool = False):
        """
        Extract text from PDF and save to CSV.
        
        Args:
            output_path (str): Path to save the CSV file
            data_processor (callable, optional): Function to process the extracted text
                into a list of dictionaries. If None, saves raw text.
            use_ocr (bool): Whether to use OCR for text extraction
        """
        text, hyperlinks = self.extract_text(use_ocr=use_ocr)
        
        if data_processor:
            data = data_processor(text, hyperlinks)
            df = pd.DataFrame(data)
        else:
            # If no processor provided, save raw text
            df = pd.DataFrame({'text': [text]})
        
        df.to_csv(output_path, index=False)
        print(f"Data successfully saved to {output_path}")

def parse_date_time(text: str) -> Tuple[str, str, str]:
    """
    Parse date and time information from text.
    Returns (date, start_time, end_time)
    """
    # Date pattern that matches "Apr 20, 2025"
    date_pattern = r'([A-Za-z]{3}\s+\d{1,2},?\s+\d{4})'
    # Time pattern that matches "2:30 PM - 4:30 PM"
    time_pattern = r'(\d{1,2}:\d{2}\s*[AP]M)\s*-\s*(\d{1,2}:\d{2}\s*[AP]M)'
    
    date = ""
    start_time = ""
    end_time = ""
    
    # Find date
    date_match = re.search(date_pattern, text)
    if date_match:
        date = date_match.group(1)
    
    # Find time
    time_match = re.search(time_pattern, text)
    if time_match:
        start_time = time_match.group(1).strip()
        end_time = time_match.group(2).strip()
    
    return date, start_time, end_time

def clean_text(text: str) -> str:
    """Clean and format text."""
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Fix common OCR artifacts
    text = text.replace('SFClimate', 'SF Climate')
    text = text.replace('Aon', 'on')
    text = text.replace('ClimateWeek', 'Climate Week')
    
    # Split camelCase words
    text = re.sub(r'(?<!^)(?=[A-Z][a-z])', ' ', text)
    
    # Fix spacing around special characters
    text = re.sub(r'(?<=\w)([&:/-])(?=\w)', r' \1 ', text)
    
    # Normalize whitespace
    text = ' '.join(text.split())
    
    # Fix capitalization while preserving proper names
    words = text.split()
    common_words = {'a', 'an', 'and', 'as', 'at', 'by', 'for', 'in', 'of', 'on', 'or', 'the', 'to', 'with'}
    proper_names = {'SF', 'California', 'San', 'Francisco', 'Climate', 'Week', 'PBS', 'CO2'}
    
    for i, word in enumerate(words):
        if word.lower() in common_words and i > 0:
            words[i] = word.lower()
        elif word in proper_names:
            continue
        elif i == 0 or word not in common_words:
            words[i] = word.title()
    
    text = ' '.join(words)
    
    # Remove trailing artifacts
    text = re.sub(r'\s*\([^)]*\)\s*$', '', text)
    text = re.sub(r'\s*[|]\s*[A-Za-z\s]+$', '', text)
    
    return text.strip()

def extract_categories(text: str) -> Tuple[str, List[str]]:
    """Extract categories from text."""
    # Standard category keywords
    category_keywords = {
        'CLIMATE ARTS AND CULTURE',
        'COMMUNICATIONS',
        'ENVIRONMENTAL JUSTICE & EQUITY',
        'BUILDINGS & INFRASTRUCTURE',
        'CARBON CAPTURE',
        'UTILIZATION',
        'STORAGE',
        'ENERGY',
        'IN-PERSON EVENT',
        'INDUSTRIAL'
    }
    
    # Clean and separate organizers from categories
    text = clean_text(text)
    categories = []
    organizers = []
    
    # Split by common separators
    parts = re.split(r'[,;|]|\band\b', text)
    
    for part in parts:
        part = part.strip()
        # Check if this part matches any category
        is_category = False
        for keyword in category_keywords:
            if keyword.lower() in part.lower():
                categories.append(keyword)
                is_category = True
                break
        if not is_category:
            organizers.append(part)
    
    # Remove duplicates while preserving order
    seen_categories = set()
    unique_categories = []
    for cat in categories:
        if cat not in seen_categories:
            seen_categories.add(cat)
            unique_categories.append(cat)
    
    return ', '.join(organizers), unique_categories

def join_split_event_names(event_details: List[str]) -> str:
    """Join event name parts that might have been split."""
    # Join all parts
    full_name = ' '.join(event_details)
    
    # Clean up artifacts
    full_name = clean_text(full_name)
    
    # Remove trailing category-like text
    full_name = re.sub(r'\s*[|]\s*[A-Za-z\s&]+$', '', full_name)
    
    # Remove duplicate words while preserving proper names
    words = full_name.split()
    seen = set()
    unique_words = []
    for word in words:
        if word.lower() not in seen or any(word in name for name in ['San Francisco', 'Climate Week', 'CO2']):
            seen.add(word.lower())
            unique_words.append(word)
    
    return ' '.join(unique_words)

def extract_url(text: str) -> str:
    """Extract URL from text."""
    # Common URL patterns
    url_patterns = [
        r'https?://[^\s<>"]+|www\.[^\s<>"]+',  # Standard URLs
        r'(?<=Register at )[^\s<>"]+',  # URLs after "Register at"
        r'(?<=RSVP: )[^\s<>"]+',  # URLs after "RSVP:"
        r'(?<=Link: )[^\s<>"]+',  # URLs after "Link:"
        r'(?<=Visit )[^\s<>"]+',  # URLs after "Visit"
    ]
    
    for pattern in url_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            url = match.group().strip('.,)')  # Clean up URL
            # Add https:// if missing
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            return url
    return ''

def event_data_processor(text: str, hyperlinks: List[Dict[str, str]] = None) -> List[Dict]:
    """Process text to extract event information."""
    events = []
    current_event = None
    seen_links = set()  # Track seen links to avoid duplicates
    
    # Split text into lines and clean them
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Check if this line contains date and time information
        if '•' in line and 'PDT' in line:
            # If we have a current event, save it
            if current_event:
                events.append(current_event)
            
            # Extract date and time from the line
            date_time_parts = line.split('•')
            date = date_time_parts[0].strip()
            time_parts = date_time_parts[1].split('-')
            start_time = time_parts[0].strip().replace('PDT', '').strip()
            end_time = time_parts[1].strip().replace('PDT', '').strip()
            
            # Start a new event
            current_event = {
                'date': date,
                'start_time': start_time,
                'end_time': end_time,
                'event_name': '',
                'organizers': '',
                'categories': '',
                'location': '',
                'link': ''
            }
            
            # Look ahead for event name and other details
            event_details = []
            j = i + 1
            while j < len(lines) and '•' not in lines[j]:
                event_details.append(lines[j])
                j += 1
            
            if event_details:
                # Get complete event name
                current_event['event_name'] = join_split_event_names(event_details)
                
                # Process remaining details
                remaining_details = event_details[len(current_event['event_name'].split('\n')):]
                organizer_details = []
                
                # Try to find a matching hyperlink
                if hyperlinks:
                    event_text = ' '.join(event_details).lower()
                    for link in hyperlinks:
                        link_text = link.get('text', '').lower()
                        url = link['url']
                        # Only use links we haven't seen before
                        if url not in seen_links and any(detail.lower() in link_text for detail in event_details):
                            current_event['link'] = url
                            seen_links.add(url)
                            break
                
                for detail in remaining_details:
                    # Check if it's a location
                    if any(loc in detail for loc in ['San Francisco', 'CA', 'California']) or \
                       (len(detail.split()) <= 4 and not re.match(r'^[A-Z\s&]+$', detail)):
                        current_event['location'] = clean_text(detail)
                    else:
                        organizer_details.append(detail)
                
                # Process organizers and categories
                if organizer_details:
                    combined_organizers = '; '.join(organizer_details)
                    organizers, categories = extract_categories(combined_organizers)
                    current_event['organizers'] = clean_text(organizers)
                    current_event['categories'] = ', '.join(categories) if categories else ''
                
                i = j - 1  # Move to the last processed line
        
        i += 1
    
    # Add the last event if exists
    if current_event:
        events.append(current_event)
    
    return events

if __name__ == "__main__":
    # Example usage
    pdf_path = "All Events _ SF Climate Week1.pdf"  # Your PDF filename
    output_path = "sf_climate_week_events.csv"
    
    try:
        extractor = PDFExtractor(pdf_path)
        # First try without OCR
        try:
            extractor.extract_to_csv(output_path, data_processor=event_data_processor, use_ocr=False)
            print(f"Successfully processed PDF and saved to {output_path}")
            print("\nFirst few rows of the CSV:")
            df = pd.read_csv(output_path)
            # Reorder columns to show link near the event name
            columns = ['date', 'start_time', 'end_time', 'event_name', 'link', 'organizers', 'categories', 'location']
            df = df[columns]
            print(df.head().to_string())
        except Exception as e:
            print(f"Direct extraction failed: {str(e)}")
            print("Trying with OCR...")
            extractor.extract_to_csv(output_path, data_processor=event_data_processor, use_ocr=True)
    except Exception as e:
        print(f"Error: {str(e)}") 