import re

def extract_general_entities(text: str) -> dict:
    """Extracts general metadata (emails, phones, URLs, dates) from any document."""
    results = {}
    
    # 1. Emails
    emails = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)
    if emails:
        results["emails"] = list(set(emails))
        
    # 2. Phone Numbers
    phones = re.findall(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text)
    if phones:
        results["phones"] = list(set(phones))
        
    # 3. URLs
    urls = re.findall(r"https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)", text)
    if urls:
        results["urls"] = list(set(urls))
        
    # 4. Dates
    # Standard format: DD/MM/YYYY, MM/DD/YYYY, YYYY-MM-DD
    dates_numeric = re.findall(r"\b\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}\b", text)
    # Textual format: June 4, 2026, 04 Jun 2026
    dates_textual = re.findall(r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b", text, re.IGNORECASE)
    
    all_dates = list(set(dates_numeric + dates_textual))
    if all_dates:
        results["dates"] = all_dates
        
    return results

def extract_invoice_info(text: str) -> dict:
    """Extracts specific invoice fields."""
    info = {
        "Vendor Name": "Not Found",
        "Invoice Number": "Not Found",
        "Invoice Date": "Not Found",
        "Due Date": "Not Found",
        "Subtotal": "Not Found",
        "Tax / VAT": "Not Found",
        "Total Amount": "Not Found"
    }
    
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    
    # 1. Vendor Name Heuristic (usually first 2 lines if not containing "invoice", date, etc.)
    for line in lines[:3]:
        cleaned = line.lower()
        if not any(x in cleaned for x in ["invoice", "date", "bill to", "tax", "tel:", "phone:", "page", "client", "customer"]):
            if len(line) > 2 and len(line) < 40:
                info["Vendor Name"] = line
                break
                
    text_lower = text.lower()
    
    # 2. Invoice Number
    inv_patterns = [
        r"invoice\s*#?\s*[:\s]*([a-zA-Z0-9\-]+)",
        r"inv\s*#?\s*[:\s]*([a-zA-Z0-9\-]+)",
        r"bill\s*no\s*[:\s]*([a-zA-Z0-9\-]+)",
        r"invoice\s*number\s*[:\s]*([a-zA-Z0-9\-]+)",
        r"invoice\s*id\s*[:\s]*([a-zA-Z0-9\-]+)"
    ]
    for pattern in inv_patterns:
        match = re.search(pattern, text_lower)
        if match:
            # Get match from original text to preserve casing
            start, end = match.span(1)
            info["Invoice Number"] = text[start:end].strip()
            break
            
    # 3. Dates (Invoice Date vs Due Date)
    date_regex = r"(\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b)"
    
    # Invoice Date (same line or next line check)
    for i, line in enumerate(lines):
        l_lower = line.lower()
        if "invoice date" in l_lower or "billing date" in l_lower or "inv date" in l_lower or ("date" in l_lower and not "due" in l_lower):
            date_match = re.search(date_regex, line, re.IGNORECASE)
            if date_match:
                info["Invoice Date"] = date_match.group(0)
                break
            elif i + 1 < len(lines):
                next_line = lines[i+1].strip()
                date_match = re.search(r"^" + date_regex + r"$", next_line, re.IGNORECASE)
                if date_match:
                    info["Invoice Date"] = date_match.group(0)
                    break
                
    # Due Date (same line or next line check)
    for i, line in enumerate(lines):
        l_lower = line.lower()
        if "due date" in l_lower or "due by" in l_lower or "payment due" in l_lower or "pay by" in l_lower:
            date_match = re.search(date_regex, line, re.IGNORECASE)
            if date_match:
                info["Due Date"] = date_match.group(0)
                break
            elif i + 1 < len(lines):
                next_line = lines[i+1].strip()
                date_match = re.search(r"^" + date_regex + r"$", next_line, re.IGNORECASE)
                if date_match:
                    info["Due Date"] = date_match.group(0)
                    break
                
    # 4. Financial amounts (Subtotal, Tax, Total)
    amount_pattern = r"(?:[\$\£\€\u20b9]\s*)?(\d{1,3}(?:[ ,.]\d{3})*[.,]\d{2}|\d+[.,]\d{2})"
    
    # Subtotal
    for i, line in enumerate(lines):
        l_lower = line.lower()
        if "subtotal" in l_lower or "sub-total" in l_lower or "net amount" in l_lower:
            match = re.search(amount_pattern, line)
            if match:
                info["Subtotal"] = match.group(0)
                break
            elif i + 1 < len(lines):
                next_match = re.search(amount_pattern, lines[i+1])
                if next_match:
                    info["Subtotal"] = next_match.group(0)
                    break
                
    # Tax / VAT
    for i, line in enumerate(lines):
        l_lower = line.lower()
        if "tax" in l_lower or "vat" in l_lower or "gst" in l_lower:
            match = re.search(amount_pattern, line)
            if match:
                info["Tax / VAT"] = match.group(0)
                break
            elif i + 1 < len(lines):
                next_match = re.search(amount_pattern, lines[i+1])
                if next_match:
                    info["Tax / VAT"] = next_match.group(0)
                    break
                
    # Total
    total_keywords = ["total due", "amount due", "net due", "grand total", "total amount", "total", "balance due", "amount to pay"]
    for keyword in total_keywords:
        found = False
        for i, line in enumerate(lines):
            l_lower = line.lower()
            if keyword in l_lower and not "subtotal" in l_lower and not "tax" in l_lower:
                match = re.search(amount_pattern, line)
                if match:
                    info["Total Amount"] = match.group(0)
                    found = True
                    break
                elif i + 1 < len(lines):
                    next_match = re.search(amount_pattern, lines[i+1])
                    if next_match:
                        info["Total Amount"] = next_match.group(0)
                        found = True
                        break
        if found:
            break
            
    # Backup: If no total was found, look for largest monetary value in lines containing total
    if info["Total Amount"] == "Not Found":
        candidates = []
        for line in lines:
            if "total" in line.lower():
                matches = re.findall(amount_pattern, line)
                for m in matches:
                    try:
                        val = float(m.replace(",", "").replace("$", "").replace("£", "").replace("€", "").replace("₹", "").strip())
                        candidates.append((val, m))
                    except ValueError:
                        pass
        if candidates:
            candidates.sort(reverse=True)
            info["Total Amount"] = candidates[0][1]
            
    return info

def extract_receipt_info(text: str) -> dict:
    """Extracts specific receipt fields."""
    info = {
        "Store Name": "Not Found",
        "Transaction Date": "Not Found",
        "Transaction Time": "Not Found",
        "Total Paid": "Not Found",
        "Payment Method": "Not Found"
    }
    
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    
    # 1. Store Name Heuristic
    if lines:
        for line in lines[:2]:
            cleaned = line.lower()
            if not any(x in cleaned for x in ["receipt", "welcome", "date", "tel", "phone"]):
                if len(line) > 2 and len(line) < 35:
                    info["Store Name"] = line
                    break
                    
    # 2. Transaction Date and Time
    time_pattern = r"\b\d{1,2}:\d{2}(?::\d{2})?\s*(?:am|pm)?\b"
    date_pattern = r"(\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b)"
    
    for line in lines:
        time_match = re.search(time_pattern, line, re.IGNORECASE)
        if time_match and info["Transaction Time"] == "Not Found":
            info["Transaction Time"] = time_match.group(0)
            
        date_match = re.search(date_pattern, line, re.IGNORECASE)
        if date_match and info["Transaction Date"] == "Not Found":
            info["Transaction Date"] = date_match.group(0)
            
    # 3. Total Paid
    amount_pattern = r"(?:[\$\£\€\u20b9]\s*)?(\d{1,3}(?:[ ,.]\d{3})*[.,]\d{2}|\d+[.,]\d{2})"
    receipt_total_kws = ["total paid", "total amount", "amount paid", "total", "net to pay", "sum", "grand total", "paid amount"]
    for keyword in receipt_total_kws:
        found = False
        for i, line in enumerate(lines):
            l_lower = line.lower()
            if keyword in l_lower and not "subtotal" in l_lower and not "tax" in l_lower and not "change" in l_lower:
                match = re.search(amount_pattern, line)
                if match:
                    info["Total Paid"] = match.group(0)
                    found = True
                    break
                elif i + 1 < len(lines):
                    next_match = re.search(amount_pattern, lines[i+1])
                    if next_match:
                        info["Total Paid"] = next_match.group(0)
                        found = True
                        break
        if found:
            break
            
    # 4. Payment Method
    pay_methods = ["cash", "visa", "mastercard", "credit", "debit", "amex", "discover", "card", "apple pay", "google pay"]
    for line in lines:
        l_lower = line.lower()
        for method in pay_methods:
            if method in l_lower:
                info["Payment Method"] = method.capitalize()
                break
        if info["Payment Method"] != "Not Found":
            break
            
    return info

def extract_certificate_info(text: str) -> dict:
    """Extracts certificate information."""
    info = {
        "Recipient Name": "Not Found",
        "Certificate Title / Award": "Not Found",
        "Issuing Organization": "Not Found",
        "Date of Issue": "Not Found"
    }
    
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    
    # 1. Title Heuristics
    title_keywords = ["certificate of completion", "certificate of appreciation", "certificate of achievement", 
                      "award of excellence", "certificate of participation", "diploma", "award of merit"]
    for line in lines[:8]:
        l_lower = line.lower()
        # Direct match check
        for kw in title_keywords:
            if kw in l_lower:
                info["Certificate Title / Award"] = line
                break
        if info["Certificate Title / Award"] != "Not Found":
            break
            
    # If not found directly, look for patterns with "certificate of"
    if info["Certificate Title / Award"] == "Not Found":
        for line in lines[:8]:
            match = re.search(r"(certificate\s+of\s+[a-zA-Z\s]+|award\s+of\s+[a-zA-Z\s]+)", line, re.IGNORECASE)
            if match:
                info["Certificate Title / Award"] = match.group(0).strip()
                break
                
    # 2. Recipient Name Heuristics
    # Try finding recipient name on the same line first using regex
    for line in lines:
        for trigger in [r"presented\s+to", r"awarded\s+to", r"proudly\s+presented\s+to", r"certifies\s+that", r"certify\s+that", r"given\s+to", r"granted\s+to", r"conferred\s+upon"]:
            match = re.search(trigger + r"\s+([A-Z][a-zA-Z\s\.\-]+)", line, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                # Clean name (e.g. remove words like "for", "on", "who", "has")
                name = re.split(r"\b(?:for|on|who|has|in|is|of|completed|successfully)\b", name, flags=re.IGNORECASE)[0].strip()
                if len(name) > 2 and len(name) < 35:
                    info["Recipient Name"] = name
                    break
        if info["Recipient Name"] != "Not Found":
            break
            
    # Fallback to checking the next lines
    if info["Recipient Name"] == "Not Found":
        recipient_triggers = ["presented to", "awarded to", "proudly presented to", "certifies that", "given to", "granted to"]
        for i, line in enumerate(lines):
            l_lower = line.lower()
            if any(trigger in l_lower for trigger in recipient_triggers):
                for offset in [1, 2]:
                    if i + offset < len(lines):
                        candidate = lines[i + offset].strip()
                        candidate = re.split(r"\b(?:for|on|who|has|in|is|of|completed|successfully)\b", candidate, flags=re.IGNORECASE)[0].strip()
                        if re.match(r"^[A-Z][a-zA-Z\s\.\-]+$", candidate) and len(candidate) > 2 and len(candidate) < 35:
                            info["Recipient Name"] = candidate
                            break
                if info["Recipient Name"] != "Not Found":
                    break
                
    # 3. Issuing Organization
    # Try common explicit phrases first
    for line in lines:
        l_lower = line.lower()
        org_phrase_match = re.search(r"\b(?:offered by|issued by|presented by|authorized by)\s+([A-Za-z0-9\s,&.\-]+)", line, re.IGNORECASE)
        if org_phrase_match:
            candidate = org_phrase_match.group(1).strip()
            if len(candidate) > 3 and len(candidate) < 60:
                info["Issuing Organization"] = candidate
                break
                
    # Try patterns next
    if info["Issuing Organization"] == "Not Found":
        org_patterns = [
            r"(university\s+of\s+[a-zA-Z\s]+)",
            r"([a-zA-Z\s]+university)",
            r"([a-zA-Z\s]+institute\s+of\s+[a-zA-Z\s]+)",
            r"([a-zA-Z\s]+association)",
            r"([a-zA-Z\s]+academy)",
            r"([a-zA-Z\s]+corporation)",
            r"([a-zA-Z\s]+foundation)",
            r"([a-zA-Z0-9\s,&.\-]+(?:\s+LLC|\s+Inc\.?|\s+Ltd\.?|\s+Co\.?|\s+Corporation|\s+Group|\s+Solutions))\b"
        ]
        for line in lines:
            for pattern in org_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match and not any(x in line.lower() for x in ["presented", "awarded", "certify", "recipient"]):
                    info["Issuing Organization"] = match.group(0).strip()
                    break
            if info["Issuing Organization"] != "Not Found":
                break
                
    # Fallback to common issuers
    if info["Issuing Organization"] == "Not Found":
        common_issuers = ["Google", "Microsoft", "Coursera", "Udemy", "Harvard", "Stanford", "MIT", "IBM", "AWS", "Amazon", "Salesforce", "Cisco", "Oracle", "DeepLearning.AI"]
        for issuer in common_issuers:
            if re.search(rf"\b{issuer}\b", text, re.IGNORECASE):
                info["Issuing Organization"] = issuer
                break
                
    # 4. Date of Issue
    # Master date regex matching:
    # 1. DD/MM/YYYY or DD-MM-YYYY (e.g. 12/01/2026)
    # 2. Month DD, YYYY (e.g. January 1, 2026 or Jan 1st, 2026)
    # 3. DD Month YYYY (e.g. 12 January 2026 or 12th Jan 2026 or 1st of January 2026)
    # 4. Month YYYY (e.g. January 2026)
    date_regex = (
        r"(?:"
        r"\b\d{1,2}[-/.]\d{1,2}[-/.]\d{2,4}\b|"
        r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2}(?:st|nd|rd|th)?\s*,\s*\d{4}\b|"
        r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2}(?:st|nd|rd|th)?\s+\d{4}\b|"
        r"\b\d{1,2}(?:st|nd|rd|th)?\s+(?:of\s+)?(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b|"
        r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b"
        r")"
    )
    date_keyword_pattern = rf"(?:date\s*of\s*issue|issued\s*on|date|completed\s*on|awarded\s*on)\s*[:\-–|\s]*\s*({date_regex})"
    
    for line in lines:
        date_match = re.search(date_keyword_pattern, line, re.IGNORECASE)
        if date_match:
            info["Date of Issue"] = date_match.group(1).strip()
            break
            
    if info["Date of Issue"] == "Not Found":
        for line in reversed(lines):
            date_match = re.search(date_regex, line, re.IGNORECASE)
            if date_match:
                info["Date of Issue"] = date_match.group(0).strip()
                break
    

    return info           
       

def extract_question_paper_info(text: str) -> dict:
    """Extracts question paper details."""
    info = {
        "Exam / Subject": "Not Found",
        "Maximum Marks": "Not Found",
        "Time Allowed": "Not Found",
        "Number of Questions": "0",
        "Sections Found": "None"
    }
    
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    if not lines:
        return info
        
    # 1. Subject / Exam
    subject_candidate = None
    for line in lines[:15]:
        l_lower = line.lower()
        if "course code" in l_lower or "course title" in l_lower or "subject" in l_lower:
            match = re.search(r"(?:course\s*code\s*&\s*course\s*title|course\s*title|subject)\s*[:\-–|]\s*(.+)", line, re.IGNORECASE)
            if match:
                subject_candidate = match.group(1).strip()
                break
                
    if subject_candidate:
        info["Exam / Subject"] = subject_candidate
    else:
        for line in lines[:10]:
            l_lower = line.lower()
            if any(kw in l_lower for kw in ["examination", "test", "semester", "paper", "class"]):
                if len(line) < 80 and len(line) > 5:
                    info["Exam / Subject"] = line
                    break
                    
    # 2. Maximum Marks
    marks_pattern = r"(?:max(?:\.|imum)?\s*marks?|total\s*marks?|maximum\s*mark?|max\.?\s*mark?|total\s*mark?)\s*[:\-–|\.\s]*\s*(\d+)"
    for line in lines[:25]:
        match = re.search(marks_pattern, line, re.IGNORECASE)
        if match:
            info["Maximum Marks"] = match.group(1)
            break
            
    # 3. Time Allowed
    for line in lines[:25]:
        label_match = re.search(r"(?:time\s*allowed|duration|time)\s*[:\-–|\s]*\s*([^|\n]+)", line, re.IGNORECASE)
        if label_match:
            val = label_match.group(1).strip()
            if any(x in val.lower() for x in ["hour", "hr", "min", "sec", "h ", "m "]):
                val = re.split(r"[|,;]", val)[0].strip()
                info["Time Allowed"] = val
                break
                
        raw_match = re.search(r"\b\d+\s*(?:hour|hr|min|sec|h|m)s?\b", line, re.IGNORECASE)
        if raw_match and info["Time Allowed"] == "Not Found":
            phrase_match = re.search(r"\b\d+\s*(?:hour|hr|min|sec|h|m)s?(?:\s*(?:and|\d+)?\s*(?:hour|hr|min|sec|h|m)s?)?\b", line, re.IGNORECASE)
            if phrase_match:
                info["Time Allowed"] = phrase_match.group(0).strip()
                break
                
    # Clean the extracted duration from coinciding marks or other labels
    if info["Time Allowed"] != "Not Found":
        # Remove anything starting from Max, Mark, Marks, etc.
        cleaned = re.split(r"\b(?:max|mark|marks|total)\b", info["Time Allowed"], flags=re.IGNORECASE)[0].strip()
        cleaned = re.sub(r"[:\-–|,\s]+$", "", cleaned).strip()
        info["Time Allowed"] = cleaned
                
    # 4. Question Count and list of questions
    q_nums = set()
    for line in lines:
        l_clean = line.strip()
        l_clean_no_pipes = l_clean.replace('|', ' ').strip()
        
        # Match digit followed by optional punctuation/spaces/pipes, then a letter
        digit_match = re.match(r"^(\d+)\s*(?:[\.\)\]|:]\s*)*([A-Za-z])", l_clean_no_pipes)
        if digit_match:
            num = int(digit_match.group(1))
            if num < 50:
                l_lower = l_clean_no_pipes.lower()
                if not any(x in l_lower for x in ["semester", "class", "duration", "max", "mark", "date", "year", "credit", "course", "faculty", "slot"]):
                    q_nums.add(num)
                    continue
                    
        # Match standard Q1, Question 2 labels
        q_label_match = re.match(r"^(?:q(?:uestion)?\b\.?\s*[:\-–]?\s*(\d+))", l_clean_no_pipes, re.IGNORECASE)
        if q_label_match:
            q_nums.add(int(q_label_match.group(1)))
            continue

    info["Number of Questions"] = str(len(q_nums)) if q_nums else "Undetected"
    
    # 5. Sections
    sections = []
    for line in lines:
        section_match = re.search(r"\b(section|part|sec)\b\.?\s*([a-gA-G1-9])\b", line, re.IGNORECASE)
        if section_match:
            sections.append(section_match.group(0).upper())
            
    if sections:
        info["Sections Found"] = ", ".join(sorted(list(set(sections))))
        
    return info

def extract_notes_info(text: str) -> dict:
    """Extracts topic structure from lecture/study notes."""
    info = {
        "Topic / Title": "Not Found",
        "Key Definitions Count": "0",
        "Key Headings": "None",
        "Bullet Points Count": "0"
    }
    
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    
    # 1. Topic
    if lines:
        for line in lines[:3]:
            if len(line) < 40 and not line.startswith(("-", "*", "1.")):
                info["Topic / Title"] = line
                break
                
    # 2. Key Definitions Count
    def_count = 0
    for line in lines:
        l_lower = line.lower()
        if "is defined as" in l_lower or "refers to" in l_lower or l_lower.startswith("definition:"):
            def_count += 1
    info["Key Definitions Count"] = str(def_count)
    
    # 3. Key Headings
    headings = []
    for line in lines:
        if len(line) < 30 and (line.isupper() or re.match(r"^(?:[I|V|X]+\.\s+|[A-Z]\.\s+)", line)):
            headings.append(line)
    if headings:
        info["Key Headings"] = ", ".join(headings[:5])
        
    # 4. Bullet Points Count
    bullet_count = 0
    for line in lines:
        if line.startswith(("-", "*", "•", "▪", "◦")):
            bullet_count += 1
    info["Bullet Points Count"] = str(bullet_count)
    
    return info

def extract_document_information(text: str, category: str) -> dict:
    """
    Primary API to extract fields.
    Invokes the specialized extractor based on the category.
    Includes general entities (emails, phones, etc.) in a combined dict.
    """
    extracted_data = {}
    
    # 1. Extract category-specific details
    if category == "Invoice":
        extracted_data = extract_invoice_info(text)
    elif category == "Receipt":
        extracted_data = extract_receipt_info(text)
    elif category == "Certificate":
        extracted_data = extract_certificate_info(text)
    elif category == "Question Paper":
        extracted_data = extract_question_paper_info(text)
    elif category == "Notes":
        extracted_data = extract_notes_info(text)
    else:
        # Default/Unknown document metadata
        extracted_data = {
            "Document Name": "Scanned Document",
            "Language Code": "en",
            "Word Count": str(len(text.split())),
            "Lines Count": str(len(text.split("\n")))
        }
        
    # 2. Append general entities as well
    general = extract_general_entities(text)
    for key, val in general.items():
        extracted_data[key.capitalize()] = ", ".join(val)
        
    return extracted_data