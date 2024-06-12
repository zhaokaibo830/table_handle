table_head_analysis_prompt_en = """
                    {text}
                    The above list contains the entire content of a table, where each element corresponds to a cell in the table. Please identify the cells that may be the header based on semantic information,. Please analyze step by step, and note that each element corresponds to a cell, so it is not possible to split and understand the content of each row.
                    """

table_head_analysis_prompt_ch = """
                    {text}
                    以上列表是一个表格的全部内容，其中每一个元素对应表格的一个单元格内容，请根据表格的语义信息找出其中可能是表头或标题的单元格。请一步一步进行分析，要注意每一个元素内容对应一个单元格，所以不能对每一行的内容进行拆分理解。
                    """

table_head_extract_prompt_en = """
                    {text}
                    Please output all headers in the form of a list, with the following template: ["Date of Birth", "Hometown"]. Just follow the template and do not require any additional content.
                    """

table_head_extract_prompt_ch = """
                    {context}
                    Based on the above content, please output all possible header or title content in the form of a list. The template is as follows: ["Date of Birth", "Hometown"], just output according to the template, no additional content is needed, and each element in the list is an element of the following list:
                    {text}
                    """

polish_prompt_en = """
            {text}
            Please polish the above content into a description that is used by humans. Try to keep it in technical terms.
            """


polish_prompt_ch = """
            {text}
            变换以上内容的描述方式。
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

fact_verification_analysis_prompt_en="""
                        {context}
                        
                        Based on the above information, please determine whether the following proposition is correct and analyze step by step.
                        {proposition}
                        """

fact_verification_judge_prompt_en = """
                        {analysis}

                        Based on the above information, please determine whether the proposition is correct. If it is correct, only ["true"] needs to be returned, and if it is not, only ["false"] needs to be returned. It is prohibited to output additional explanations.
                        """







