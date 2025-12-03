"""
Enhanced Section Validation Script
Comprehensive checks for all output files
"""
import json
import os


def check_sections():
    """
    Comprehensive validation with detailed reporting.
    Checks all deliverables and metrics.
    """
    
    # Define paths
    project_root = os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
    output_dir = os.path.join(project_root, "data", "output")
    
    toc_file = os.path.join(output_dir, "usb_pd_toc.jsonl")
    spec_file = os.path.join(output_dir, "usb_pd_spec.jsonl")
    validation_file = os.path.join(
        output_dir,
        "validation_report.json"
    )
    
    # Check file existence
    files_status = {
        "TOC": os.path.exists(toc_file),
        "Spec": os.path.exists(spec_file),
        "Validation": os.path.exists(validation_file)
    }
    
    if not files_status["TOC"] or not files_status["Spec"]:
        print("="*70)
        print("❌ ERROR: Required files missing!")
        print("="*70)
        if not files_status["TOC"]:
            print(f"Missing: {toc_file}")
        if not files_status["Spec"]:
            print(f"Missing: {spec_file}")
        print("\nRun: python src/usb_pd_parser.py")
        print("="*70)
        return

    # Load and analyze files
    print("="*70)
    print("USB PD PARSER - VALIDATION REPORT")
    print("="*70)
    
    # Count TOC sections
    toc_count = 0
    toc_samples = []
    with open(toc_file, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if line.strip():
                toc_count += 1
                if i < 3:
                    toc_samples.append(json.loads(line))

    # Count spec sections and analyze content
    spec_count = 0
    spec_samples = []
    total_content_length = 0
    non_empty_count = 0
    
    with open(spec_file, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if line.strip():
                spec_count += 1
                entry = json.loads(line)
                content = entry.get("content", "")
                total_content_length += len(content)
                
                if content.strip():
                    non_empty_count += 1
                
                if i < 3:
                    spec_samples.append(entry)
    
    # Calculate content metrics
    avg_content_length = (
        total_content_length / spec_count 
        if spec_count > 0 else 0
    )
    content_quality_pct = (
        non_empty_count / spec_count * 100 
        if spec_count > 0 else 0
    )
    
    # Load validation report if exists
    validation_data = None
    if files_status["Validation"]:
        with open(validation_file, "r", encoding="utf-8") as f:
            validation_data = json.load(f)

    # Print comprehensive report
    print("\n📊 FILE STATUS:")
    for name, exists in files_status.items():
        status = "✓ Found" if exists else "✗ Missing"
        print(f"  {status:12} - {name}")
    
    print("\n📈 EXTRACTION STATISTICS:")
    print(f"  TOC Sections:        {toc_count:,}")
    print(f"  Content Sections:    {spec_count:,}")
    print(f"  Sections Match:      "
          f"{'✓ Yes' if toc_count == spec_count else '✗ No'}")
    
    print(f"\n📝 CONTENT QUALITY:")
    print(f"  Avg Content Length:  {avg_content_length:.0f} chars")
    print(f"  Non-Empty Sections:  {non_empty_count:,}")
    print(f"  Content Quality:     {content_quality_pct:.1f}%")
    
    if validation_data:
        print("\n📋 VALIDATION REPORT ANALYSIS:")
        
        summary = validation_data.get("summary", {})
        page_cov = summary.get("page_coverage", {})
        
        # Page Coverage (CRITICAL METRIC)
        total_pages = page_cov.get("total_pages", 0)
        pages_covered = page_cov.get("pages_covered", 0)
        coverage_pct = page_cov.get("coverage_percentage", 0)
        
        print(f"\n  📄 Page Coverage:")
        print(f"    Total Pages:       {total_pages:,}")
        print(f"    Pages Covered:     {pages_covered:,}")
        print(f"    Pages Missing:     "
              f"{page_cov.get('pages_missing', 0):,}")
        print(f"    Coverage:          {coverage_pct}%")
        
        # Status indicator
        if coverage_pct >= 95:
            cov_status = "✓ EXCELLENT"
        elif coverage_pct >= 80:
            cov_status = "✓ GOOD"
        elif coverage_pct >= 60:
            cov_status = "⚠ FAIR"
        else:
            cov_status = "✗ POOR"
        print(f"    Status:            {cov_status}")
        
        # Content Analysis
        content_analysis = validation_data.get(
            "content_analysis", {}
        )
        print(f"\n  📊 Content Analysis:")
        print(f"    With Content:      "
              f"{content_analysis.get('sections_with_content', 0):,}")
        print(f"    Without Content:   "
              f"{content_analysis.get('sections_without_content', 0):,}")
        print(f"    Avg Length:        "
              f"{content_analysis.get('average_content_length', 0):.0f}")
        
        # TOC Analysis
        toc_analysis = validation_data.get("toc_analysis", {})
        print(f"\n  🗂️  TOC Analysis:")
        print(f"    Total Sections:    "
              f"{toc_analysis.get('total_sections', 0):,}")
        print(f"    Hierarchy Levels:  "
              f"{toc_analysis.get('hierarchy_levels', 0)}")
        print(f"    Max Depth:         "
              f"{toc_analysis.get('max_depth', 0)}")
        
        # Detailed Metrics
        metrics = validation_data.get("detailed_metrics", {})
        if metrics:
            print(f"\n  🎯 Quality Metrics:")
            print(f"    Page Coverage:     "
                  f"{metrics.get('page_coverage_percentage', 0)}%")
            print(f"    Content Quality:   "
                  f"{metrics.get('content_quality_percentage', 0):.1f}%")
            print(f"    Overall Score:     "
                  f"{metrics.get('overall_quality_score', 0):.1f}%")
        
        # Overall Status
        status = validation_data.get("validation_status", "UNKNOWN")
        print(f"\n  ✨ Validation Status: {status}")
    
    # Sample Data
    print("\n🔍 SAMPLE DATA (First 3 entries):")
    
    print("\n  TOC Sample:")
    for i, entry in enumerate(toc_samples, 1):
        sec_id = entry.get("section_id", "N/A")
        title = entry.get("title", "N/A")[:40]
        page = entry.get("page", "N/A")
        print(f"    {i}. [{sec_id}] {title}... (p.{page})")
    
    print("\n  Content Sample:")
    for i, entry in enumerate(spec_samples, 1):
        sec_id = entry.get("section_id", "N/A")
        content = entry.get("content", "N/A")[:40]
        length = len(entry.get("content", ""))
        print(f"    {i}. [{sec_id}] {content}... ({length} chars)")
    
    print("\n" + "="*70)
    
    # Determine overall status
    if toc_count > 5000 and spec_count > 5000:
        if validation_data:
            status = validation_data.get(
                "validation_status", "UNKNOWN"
            )
            metrics = validation_data.get("detailed_metrics", {})
            overall = metrics.get("overall_quality_score", 0)
            
            if status == "EXCELLENT" or overall >= 90:
                print("✓ SUCCESS: EXCELLENT extraction quality!")
                print(f"  Overall Score: {overall:.1f}%")
            elif status == "GOOD" or overall >= 75:
                print("✓ SUCCESS: GOOD extraction quality!")
                print(f"  Overall Score: {overall:.1f}%")
            else:
                print("⚠ PARTIAL: Extraction completed with "
                      "warnings.")
                print(f"  Overall Score: {overall:.1f}%")
        else:
            print("✓ SUCCESS: Files generated!")
            print("⚠ WARNING: Validation report missing.")
    else:
        print("✗ ERROR: Insufficient sections extracted.")
        print(f"  Expected: >5000, Got: TOC={toc_count}, "
              f"Content={spec_count}")
    
    print("="*70)


if __name__ == "__main__":
    check_sections()