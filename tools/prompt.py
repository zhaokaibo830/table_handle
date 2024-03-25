table_head_analysis_prompt = """
                    {text}
                    The above is the cell content of a table. Please use the semantic information to find the cells that may be the header. Please analyze step by step. Please note that each row of content corresponds to a cell, so the content of each row cannot be separated and understood.
                    """

table_head_extract_prompt = """
                    {text}
                    Please output the header in list form. The template is as follows: ["Date of Birth", "Place of Place"]. You only need to output according to the template, no other extra content is required.
                    """

polish_prompt = """
            {text}
            Please polish the above content into a description that is used by humans. Try to keep it in technical terms.
            """

sub_table_extract_prompt = """
            {whole_caption}
            The above is a complete description of a complex table. Please polish the following sub-table description based on the above content:
            {i_caption}
            """