from apps.testrail_report.xlsxwriter_wrapper import SpreadSheetWriter


    
def export_xlsx(save_path: str, project_name: str, cases: [dict]) -> None:   
    with SpreadSheetWriter(save_path) as writer:
        headers = ['Sr. No.', 'Test Case ID', 'Automation Type', 'Passed', 'Failed']
        name_format = writer.format(bold=True, font_size=14)
        writer.span_col(0, 0, len(headers), project_name, name_format)
        
        row = 1
        
        # set up bold headers
        for col, header in enumerate(headers):
            writer.write(row, col, header, bold=True, align='center', vertical_align='top')
        row += 1
        
        # set widths of each column
        writer.set_column(headers.index('Test Case ID'), width=15)
        writer.set_column(headers.index('Automation Type'), width=15)
        writer.set_column(headers.index('Passed'), width=30)
        writer.set_column(headers.index('Failed'), width=30)
        
        serial_number = 1
        
        # populate data
        for case in cases:
            case_id = case['id']
            automation_type = case['custom_automation_type']
            
            writer.write(row, 0, serial_number)
            writer.write(row, 1, case_id)
            writer.write(row, 2, automation_type)
            
            get_fields = lambda header: '\n'.join(field for field in case[header])
            writer.write(row, 3, get_fields('Passed'), vertical_align='top')
            writer.write(row, 4, get_fields('Failed'), vertical_align='top')
            
            serial_number += 1
            row += 1
                
                

if __name__ == '__main__':
    pass

