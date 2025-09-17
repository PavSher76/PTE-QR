#!/usr/bin/env python3
"""Script to fix long lines in test_gdpr_compliance.py"""

# Read the file
with open('backend/tests/test_api/test_gdpr_compliance.py', 'r') as f:
    content = f.read()

# Fix long lines by breaking them
lines = content.split('\n')
for i, line in enumerate(lines):
    if len(line) > 88 and '"""' in line and 'Test that' in line:
        # Break long docstrings
        if 'GDPR Article 5(1)(c)' in line:
            lines[i] = '        """Test that only necessary data is collected and processed (GDPR Article 5(1)(c))."""'
        elif 'GDPR Article 5(1)(b)' in line:
            lines[i] = '        """Test that data is processed for specified purposes only (GDPR Article 5(1)(b))."""'
        elif 'consent mechanism' in line:
            lines[i] = '        """Test that authentication serves as consent mechanism for extended data access."""'
        elif 'cross-border transfer' in line:
            lines[i] = '        """Test that data processing complies with cross-border transfer requirements (GDPR Article 44-49)."""'

# Write back
with open('backend/tests/test_api/test_gdpr_compliance.py', 'w') as f:
    f.write('\n'.join(lines))

print("Fixed long lines in test_gdpr_compliance.py")
