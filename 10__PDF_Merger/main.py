#!/usr/bin/env python3
"""
PDF Merger Tool Backend
Merges multiple PDF files into a single PDF document
"""

import sys
import json
import tempfile
import os
from pathlib import Path
from PyPDF2 import PdfMerger, PdfReader


def sanitize_filename(filename):
    """Sanitize filename to prevent path traversal"""
    return "".join(c for c in filename if c.isalnum() or c in (' ', '.', '_', '-')).rstrip()


def merge_pdfs(pdf_files_data):
    """
    Merge multiple PDF files into one
    
    Args:
        pdf_files_data: List of dicts with 'file_path' and 'order' keys
        
    Returns:
        Path to the merged PDF file
    """
    # Sort files by order
    sorted_files = sorted(pdf_files_data, key=lambda x: x['order'])
    
    # Create PDF merger
    merger = PdfMerger()
    
    try:
        # Add each PDF to the merger
        for file_data in sorted_files:
            file_path = file_data['file_path']
            
            # Validate PDF file
            try:
                reader = PdfReader(file_path)
                if len(reader.pages) == 0:
                    raise ValueError(f"PDF file {file_path} has no pages")
                
                merger.append(file_path)
                print(f"Added: {file_path} ({len(reader.pages)} pages)", file=sys.stderr)
            except Exception as e:
                raise ValueError(f"Error reading PDF {file_path}: {str(e)}")
        
        # Create output file
        output_fd, output_path = tempfile.mkstemp(suffix='.pdf', prefix='merged_')
        os.close(output_fd)
        
        # Write merged PDF
        merger.write(output_path)
        merger.close()
        
        print(f"Merged {len(sorted_files)} PDFs successfully", file=sys.stderr)
        return output_path
        
    except Exception as e:
        merger.close()
        raise Exception(f"Failed to merge PDFs: {str(e)}")


def main():
    """Main entry point for PDF merger tool"""
    try:
        # Read input from stdin (JSON format)
        input_data = sys.stdin.read()
        data = json.loads(input_data)
        
        # Extract PDF files data
        # Expected format: {"files": [{"file_path": "path", "order": 0}, ...]}
        if 'files' not in data or not isinstance(data['files'], list):
            raise ValueError("Invalid input format. Expected 'files' array.")
        
        if len(data['files']) < 2:
            raise ValueError("At least 2 PDF files are required for merging.")
        
        pdf_files_data = data['files']
        
        # Validate all files exist
        for file_data in pdf_files_data:
            if 'file_path' not in file_data:
                raise ValueError("Each file must have 'file_path'")
            if 'order' not in file_data:
                raise ValueError("Each file must have 'order'")
            
            file_path = file_data['file_path']
            if not os.path.exists(file_path):
                raise ValueError(f"File not found: {file_path}")
            if not file_path.lower().endswith('.pdf'):
                raise ValueError(f"File is not a PDF: {file_path}")
        
        # Merge PDFs
        output_path = merge_pdfs(pdf_files_data)
        
        # Return success response with output file path
        response = {
            "success": True,
            "output_file": output_path,
            "total_files": len(pdf_files_data),
            "message": f"Successfully merged {len(pdf_files_data)} PDF files"
        }
        
        print(json.dumps(response))
        sys.exit(0)
        
    except json.JSONDecodeError as e:
        error_response = {
            "success": False,
            "error": f"Invalid JSON input: {str(e)}"
        }
        print(json.dumps(error_response))
        sys.exit(1)
        
    except ValueError as e:
        error_response = {
            "success": False,
            "error": str(e)
        }
        print(json.dumps(error_response))
        sys.exit(1)
        
    except Exception as e:
        error_response = {
            "success": False,
            "error": f"Unexpected error: {str(e)}"
        }
        print(json.dumps(error_response))
        sys.exit(1)


if __name__ == "__main__":
    main()

