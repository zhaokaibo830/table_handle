table_head_analysis_prompt = """
                    {context}
                    以上是一个表格的单元格内容，请根据语义信息找出其中可能是表头的单元格,。请一步一步进行分析，要注意每一行内容对应一个单元格，所以不能对每一行的内容进行拆分理解。
                    """

table_head_extract_prompt = """
                    {context}
                    请对表头以列表形式输出，模板如下：["出生日期","籍贯"]，只需要按照模板输出，不需要其他多余内容
                    """

polish_prompt = """
            {context}
            请把以上内容润色成人类习惯的描述方式。
            """

sub_table_extract_prompt = """
            {whole_caption}
            以上是一个完整的复杂表格描述。请根据以上内容对如下子表描述的进行润色:
            {i_caption}
            """
