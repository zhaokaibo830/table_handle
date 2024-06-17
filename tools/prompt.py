table_head_analysis_prompt_en = """
                    {text}
                    The above is the cell content of a table. Please use the semantic information to find the cells that may be the header. Please analyze step by step. Please note that each row of content corresponds to a cell, so the content of each row cannot be separated and understood.
                    """

table_head_analysis_prompt_ch = """
                    {text}
                    以上是一个表格的单元格内容，请根据语义信息找出其中可能是表头的单元格,。请一步一步进行分析，要注意每一行内容对应一个单元格，所以不能对每一行的内容进行拆分理解。
                    """

table_head_extract_prompt_en = """
                    {text}
                    Please output the header in list form. The template is as follows: ["Date of Birth", "Place of Place"]. You only need to output according to the template, no other extra content is required.
                    """

table_head_extract_prompt_ch = """
                    {text}
                    请对表头以列表形式输出，模板如下：["出生日期","籍贯"]，只需要按照模板输出，不需要其他多余内容
                    """

polish_prompt_en = """
            {text}
            Please polish the above content into a description that is used by humans. Try to keep it in technical terms.
            """

polish_prompt_ch = """
            {text}
            请把以上内容润色成人类习惯的描述方式。
            """

sub_table_extract_prompt_en = """
            {whole_caption}
            The above is a complete description of a complex table. Please polish the following sub-table description based on the above content:
            {i_caption}
            """

sub_table_extract_prompt_ch = """
            {whole_caption}
            以上是一个完整的复杂表格描述。请根据以上内容对如下子表描述的进行润色:
            {i_caption}
            """

fact_verification_analysis_prompt_en = """
                        {context}

                        Based on the above information, please determine whether the following proposition is correct and analyze step by step.
                        {proposition}
                        """

fact_verification_judge_prompt_en = """
                        {analysis}

                        Based on the above information, please determine whether the proposition is correct. If it is correct, only ["true"] needs to be returned, and if it is not, only ["false"] needs to be returned. It is prohibited to output additional explanations.
                        """







