from apps.case_report.xlsxwriter_wrapper import SpreadSheetWriter
    
def export_xlsx(save_path: str, project_name: str, cases: [dict]) -> None:   
    with SpreadSheetWriter(save_path) as writer:
        headers = ['Sr. No.', 'Test Case ID', 'Test Case Name', 'Section Name', 'Suite Name', 'Automation Type']
        name_format = writer.format(bold=True, font_size=14)
        writer.span_col(0, 0, len(headers), project_name, name_format)
        
        row = 1
        
        # set up bold headers
        for col, header in enumerate(headers):
            writer.write(row, col, header, bold=True, align='center', vertical_align='top')
        row += 1
        
        # set widths of each column
        writer.set_column(headers.index('Test Case ID'), width=15)
        writer.set_column(headers.index('Test Case Name'), width=60)
        writer.set_column(headers.index('Section Name'), width=60)
        writer.set_column(headers.index('Suite Name'), width=60)
        writer.set_column(headers.index('Automation Type'), width=60)
        
        serial_number = 1
        
        # populate data
        for case in cases:
            case_id = str(case['id'])
            case_name= case['title']
            section_name= case['section']
            suite_name= case['suite']
            auto_type= case['custom_automation_type']
            
            writer.write(row, 0, serial_number)
            writer.write_url(row, 1, 'https://gdcqatestrail01/testrail/index.php?/cases/view/' + case_id, case_id, case_id)
            writer.write(row, 2, case_name)
            writer.write(row, 3, section_name)
            writer.write(row, 4, suite_name)
            writer.write(row, 5, auto_type)
                      
            serial_number += 1
            row += 1
                                

if __name__ == '__main__':
    pass

