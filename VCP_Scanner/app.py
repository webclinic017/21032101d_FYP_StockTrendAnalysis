import OriginalVCP_Module as original_vcp_scanner
from finvizfinance.quote import finvizfinance 
import pandas as pd
import joblib 
from tqdm import tqdm
def save_chart(ticker):
    stock = finvizfinance(ticker)
    stock.ticker_charts(out_dir = 'StockChart')

def get_Original_VCP_scan_result():
    writer = pd.ExcelWriter('Original_VCP_Scan_Result.xlsx')
    Original_scan_data = joblib.load('Original_VCP_scan_result.pkl')
    numberOfVCPStock = 0
    MeanOfProfitbilty = ({
    'Stock_Symbol':[],
    'Result_1_mean':[],
    'Result_3_mean' :[],
    'Result_5_mean':[],
    'Result_7_mean':[],
    'Result_20_mean':[]
               })
    df = pd.DataFrame(MeanOfProfitbilty)
    for data in tqdm(Original_scan_data):
        if data['analysis'] is not None:
            numberOfVCPStock+=1
            new_row = {
                'Stock_Symbol':[data['stock']],
                'Result_1_mean':[data['analysis']['Result_1'].mean()],
                'Result_3_mean' :[data['analysis']['Result_3'].mean()],
                'Result_5_mean':[data['analysis']['Result_5'].mean()],
                'Result_7_mean':[data['analysis']['Result_7'].mean()],
                'Result_20_mean':[data['analysis']['Result_20'].mean()]
                }
            new_df = pd.DataFrame(new_row)
            df = pd.concat([df, new_df], ignore_index=True)
            #save_chart(data['stock'])
            data['analysis'].describe().to_excel(writer, data['stock'])
    writer.close()
    print('Original_VCP_ScanResult is written successfully to Excel Sheet.')
    print('----------------------------------------------')
    print('Best Result_1_mean of Original') 
    print(df.sort_values(by=['Result_1_mean'], ascending=(False)).head(1))
    print('----------------------------------------------')
    print('Best Result_3_mean of Original')
    print(df.sort_values(by=['Result_3_mean'], ascending=(False)).head(1))
    print('----------------------------------------------')
    print('Best Result_5_mean of Original')
    print(df.sort_values(by=['Result_5_mean'], ascending=(False)).head(1))
    print('----------------------------------------------')
    print('Best Result_7_mean of Original')
    print(df.sort_values(by=['Result_7_mean'], ascending=(False)).head(1))
    print('----------------------------------------------')
    print('Best Result_20_mean of Original')
    print(df.sort_values(by=['Result_20_mean'], ascending=(False)).head(1))
    print('----------------------------------------------')
    print('Worst Result_1_mean of Original') 
    print(df.sort_values(by=['Result_1_mean'], ascending=(True)).head(1))
    print('----------------------------------------------')
    print('Worst Result_3_mean of Original')
    print(df.sort_values(by=['Result_3_mean'], ascending=(True)).head(1))
    print('----------------------------------------------')
    print('Worst Result_5_mean of Original')
    print(df.sort_values(by=['Result_5_mean'], ascending=(True)).head(1))
    print('----------------------------------------------')
    print('Worst Result_7_mean of Original')
    print(df.sort_values(by=['Result_7_mean'], ascending=(True)).head(1))
    print('----------------------------------------------')
    print('Worst Result_20_mean of Original')
    print(df.sort_values(by=['Result_20_mean'], ascending=(True)).head(1))
    print('----------------------------------------------')
    print(df.describe())
    print('(Original)Number of haveing VCP Stock: ', numberOfVCPStock)
    
def get_HVIDYA_VCP_scan_result():
    writer = pd.ExcelWriter('HVIDYA_VCP_Scan_Result.xlsx')
    HVIDYA_scan_data = joblib.load('HVIDYA_VCP_scan_result.pkl')
    numberOfVCPStock = 0
    MeanOfProfitbilty = ({
    'Stock_Symbol':[],
    'Result_1_mean':[],
    'Result_3_mean' :[],
    'Result_5_mean':[],
    'Result_7_mean':[],
    'Result_20_mean':[]
               })
    df = pd.DataFrame(MeanOfProfitbilty)
    for data in tqdm(HVIDYA_scan_data):
        if data['analysis'] is not None:
            numberOfVCPStock+=1
            new_row = {
                'Stock_Symbol':[data['stock']],
                'Result_1_mean':[data['analysis']['Result_1'].mean()],
                'Result_3_mean' :[data['analysis']['Result_3'].mean()],
                'Result_5_mean':[data['analysis']['Result_5'].mean()],
                'Result_7_mean':[data['analysis']['Result_7'].mean()],
                'Result_20_mean':[data['analysis']['Result_20'].mean()]
                }
            new_df = pd.DataFrame(new_row)
            df = pd.concat([df, new_df], ignore_index=True)
            #save_chart(data['stock'])
            data['analysis'].describe().to_excel(writer, data['stock'])
    writer.close()
    
    print('HVIDYA_VCP_ScanResult is written successfully to Excel Sheet.')
    print('----------------------------------------------')
    print('Best Result_1_mean of HVIDYA')
    print(df.sort_values(by=['Result_1_mean'], ascending=(False)).head(1))
    print('----------------------------------------------')
    print('Best Result_3_mean of HVIDYA')
    print(df.sort_values(by=['Result_3_mean'], ascending=(False)).head(1))
    print('----------------------------------------------')
    print('Best Result_5_mean of HVIDYA')
    print(df.sort_values(by=['Result_5_mean'], ascending=(False)).head(1))
    print('----------------------------------------------')
    print('Best Result_7_mean of HVIDYA')
    print(df.sort_values(by=['Result_7_mean'], ascending=(False)).head(1))
    print('----------------------------------------------')
    print('Best Result_20_mean of HVIDYA')
    print(df.sort_values(by=['Result_20_mean'], ascending=(False)).head(1))
    print('----------------------------------------------')
    print('Worst Result_1_mean of HVIDYA')
    print(df.sort_values(by=['Result_1_mean'], ascending=(True)).head(1))
    print('----------------------------------------------')
    print('Worst Result_3_mean of HVIDYA')
    print(df.sort_values(by=['Result_3_mean'], ascending=(True)).head(1))
    print('----------------------------------------------')
    print('Worst Result_5_mean of HVIDYA')
    print(df.sort_values(by=['Result_5_mean'], ascending=(True)).head(1))
    print('----------------------------------------------')
    print('Worst Result_7_mean of HVIDYA')
    print(df.sort_values(by=['Result_7_mean'], ascending=(True)).head(1))
    print('----------------------------------------------')
    print('Worst Result_20_mean of HVIDYA')
    print(df.sort_values(by=['Result_20_mean'], ascending=(True)).head(1))
    print('----------------------------------------------')
    print(df.describe())
    print('(HVIDYA)Number of haveing VCP Stock: ', numberOfVCPStock)
    
if __name__ == '__main__':
    get_HVIDYA_VCP_scan_result()
    get_Original_VCP_scan_result()
    

            
        







