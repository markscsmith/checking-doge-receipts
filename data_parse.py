import os
import glob
from bs4 import BeautifulSoup
import pandas as pd
import tqdm
import re

def parse_html_files(directory):
    html_files = glob.glob(os.path.join(directory, 'fpds_content_*.html'))
    
    # Map field labels to a tuple: (HTML tag, name attribute, default value)
    # (This is a subset of the FPDS-NG Data Dictionary. Extend as needed.)
    fields = {
        "Procurement Instrument Identifier": ("input", "PIID", "N/A"),
        "Modification Number": ("input", "modNumber", ""),
        "Referenced PIID": ("input", "referencedPIID", ""),
        "Transaction Number": ("input", "transactionNumber", ""),
        "Solicitation Identifier": ("input", "solicitationID", ""),
        "Agency Identifier": ("input", "agencyID", ""),
        "Referenced IDV Modification Number": ("input", "idvModNumber", "0"),
        "Referenced IDV Agency Identifier": ("input", "idvAgencyID", ""),
        
        # Dates
        "Date Signed": ("input", "signedDate", "No Date"),
        "Effective Date": ("input", "effectiveDate", ""),
        "Current Completion Date": ("input", "awardCompletionDate", ""),
        "Ultimate Completion Date": ("input", "estimatedUltimateCompletionDate", ""),
        "IDV Last Date to Order": ("input", "solicitationDate", ""),
        "Date/Time Stamp Accepted": ("input", "lastModifiedDate", ""),
        
        # Dollar Values
        "Base And All Options Value": ("input", "ultimateContractValue", "0"),
        "Base And Exercised Options Value": ("input", "baseAndExercisedOptionsValue", "0"),
        "Action Obligation": ("input", "obligatedAmount", "0"),
        "Total Action Obligation": ("input", "totalObligatedAmount", "0"),
        "Total Base And Exercised Options Value": ("input", "totalBaseAndExercisedOptionsValue", "0"),
        # Additional dollar fields can be added here
        
        # Purchaser Information (if available)
        "Contracting Office Agency Name": ("input", "contractingOfficeAgencyName", "No Name"),
        "Contracting Office Code": ("input", "contractingOfficeID", ""),
        "Program/Funding Agency Code": ("input", "fundingRequestingAgencyID", ""),
        "Program/Funding Office Code": ("input", "fundingRequestingOfficeID", ""),
        "Foreign Funding": ("select", "foreignFunding", ""),
        "Source UserID": ("input", "sourceUserID", ""),
        
        # Contract Marketing Data (if available)
        "Web Site URL": ("input", "websiteURL", ""),
        "Who Can Use": ("input", "whoCanUse", ""),
        "Maximum Order Limit": ("input", "maximumOrderLimit", "0"),
        "Fee for Use of Service": ("select", "typeOfFeeForUseOfService", ""),
        "Fixed Fee Value": ("input", "fixedFeeValue", "0"),
        "Fee Range Lower Value": ("input", "feeRangeLowerValue", "0"),
        "Fee Range Upper Value": ("input", "feeRangeUpperValue", "0"),
        "Ordering Procedure": ("textarea", "orderingProcedure", ""),
        "Fee Paid for Use of IDV": ("input", "feePaidForUseOfService", "0"),
        
        # Contract Information (if available)
        "Type of Contract": ("select", "typeOfContractPricing", ""),
        "Undefinitized Action": ("select", "undefinitizedAction", ""),
        "Multi Year Contract": ("select", "multiYearContract", ""),
        "Type of IDC": ("select", "typeOfIDC", ""),
        "Major Program": ("input", "majorProgramCode", ""),
        "Contingency, Humanitarian, or Peacekeeping Operation": ("select", "contingencyHumanitarianPeacekeepingOperation", ""),
        "Cost or Pricing Data": ("select", "costOrPricingData", ""),
        "Contract Financing": ("select", "contractFinancing", ""),
        "Cost Accounting Standards Clause": ("select", "costAccountingStandardsClause", ""),
        "Purchase Card as Payment Method": ("select", "purchaseCardAsPaymentMethod", ""),
        "Program Acronym": ("input", "programAcronym", ""),
        "Number of Actions": ("input", "numberOfActions", ""),
        "National Interest Action": ("select", "nationalInterestAction", ""),
        
        # Product or Service Information (if available)
        "Product/Service Code": ("input", "productOrServiceCode", "No Code"),
        "Product/Service Description": ("input", "productOrServiceCodeDescription", "No Description"),
        "Program, System, or Equipment Code": ("input", "systemEquipmentCode", ""),
        "DoD Claimant Program Code": ("input", "claimantProgramCode", ""),
        "Information Technology Commercial Item Category": ("select", "informationTechnologyCommercialItemCategory", ""),
        
        # Contractor Data (if available)
        "DUNS Number": ("input", "dunsNumber", ""),
        "Contractor Name": ("input", "contractorName", ""),
        "Principal Place of Performance State": ("input", "placeStateCode", ""),
        "Principal Place of Performance Location": ("input", "placeLocationCode", ""),
        "Principal Place of Performance Country": ("input", "placeCountryCode", ""),
        "Principal Place of Performance Name": ("input", "principalPlaceOfPerformanceName", ""),
        "Country of Product or Service Origin": ("input", "countryOfOrigin", ""),
        "Congressional District - Contractor": ("input", "congressionalDistrictContractor", ""),
        "Congressional District - Place of Performance": ("input", "congressionalDistrict", ""),
        "Place of Manufacture": ("input", "placeOfManufacture", ""),
        "Place Of Performance Zip Code": ("input", "placeOfPerformanceZIPCode", ""),
        "Place Of Performance Zip Code Extension": ("input", "placeOfPerformanceZIPCode4", "")
    }
    
    data = []
    
    for file in tqdm.tqdm(html_files):
        with open(file, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
            row = {'File': os.path.basename(file)}
            
            for label, (tag, name_attr, default) in fields.items():
                element = soup.find(tag, {'name': name_attr})
                if element:
                    if tag == "textarea":
                        value = element.text.strip()
                    else:
                        value = element.get("value", default)
                else:
                    value = default
                row[label] = value
            data.append(row)
    
    df = pd.DataFrame(data)
    
    # Convert date fields to datetime where applicable
    date_fields = ["Date Signed", "Effective Date", "Current Completion Date", "Ultimate Completion Date", "IDV Last Date to Order"]
    for field in date_fields:
        df[field] = pd.to_datetime(df[field], errors='coerce')
    
    # Define a list of fields that are dollar amounts (we remove $ and commas)
    currency_fields = [
        "Ultimate Contract Value", "Total Ultimate Contract Value",
        "Base And All Options Value", "Base And Exercised Options Value",
        "Action Obligation", "Total Action Obligation", "Total Base And Exercised Options Value",
        "Fixed Fee Value", "Fee Range Lower Value", "Fee Range Upper Value",
        "Maximum Order Limit", "Fee Paid for Use of IDV"
    ]
    for field in currency_fields:
        if field in df.columns:
            # Remove common currency formatting
            df[field] = df[field].apply(lambda x: re.sub(r'[\$,]', '', x) if isinstance(x, str) else x)
            df[field] = pd.to_numeric(df[field], errors='coerce').round(2)
    
    return df

if __name__ == "__main__":
    directory = os.path.join(os.path.dirname(__file__), "data")
    df = parse_html_files(directory)
    print(df)
    df.to_csv(os.path.join(os.path.dirname(__file__), 'parsed_data.csv'), index=False)