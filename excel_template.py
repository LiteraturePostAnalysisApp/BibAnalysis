# Filename: excel_template.py
"""
This list represents the data extraction operations for an Excel template.
Each tuple in the list contains the following information:
- Extraction type: 'single' or 'multi'
- Column(s) to extract data from [beginning, end] (inclusive)
- Data category or categories
- Additional information (optional)

The data extraction operations are used to define the structure and content of the Excel template for data analysis.

Example usage:
- For a single extraction operation:
    ('single', 'A', 'ID')
    This will extract data from column A and assign it to the 'ID' category.

- For a multi extraction operation:
    ('multi', ['C', 'Y'], 'PublishYear')
    This will extract data from columns C to Y (inclusive) and assign it to the 'PublishYear' category.

Note: The 'single' extraction type is used for extracting data from a single column, while the 'multi' extraction type is used for extracting data from multiple columns.
"""

data_extraction_operations = [
    ('single', 'A', 'ID'),
    ('single', 'B', 'Authors'),
    ('multi',['C', 'Y'], 'PublishYear'),
    ('multi',['Z', "AB"], ["Component", "Structure", "Regional(Network)"], 'Scale'),
    ('multi',["AC", "AQ"], ["RSM", "ANN", "DL", "SVM", "KNN", "LR", "NB", "DT", "RF", "GP", "DA", "GM", "Boost", "Hybrid", "Other"], 'ML methods'),
    ('multi',["AR", "AV"], ["Classification", "Regression", "Clustering", "Dimensionality Reduction", "Decision-making"], 'Task'),
    ('multi',["AW", "AY"], ["Computational or theoretical analysis", "Field measurement", "Laboratory testing"], 'Data resource'),
    ('multi',["AZ", "BD"], ["Response/demand modeling", "Capacity modeling", "Damage modeling", "Risk assessment", "Resilience analysis"], 'Topic'),
    ('multi',["BE", "BM"], ["Normal operation or event-independent", "Earthquake", "Landslide and debris flow", "Flood and scour", "Extreme wind", "Storm Surge or wave loads", "Fire or Wildfire", "Collision", "Multi-hazard or not"], 'Event'),
    ('single',"BQ", 'Full_Citation', 'single')
]
