# openai_client.py

from openai import OpenAI
import auth

client = OpenAI(api_key=auth.OPENAI_API_KEY)

def extract_sku_name(sku, email_body, criteria_description):
    # Context-aware prompt
    if criteria_description == "Refund Initiated":
        prompt = f"""
        Extract the exact product name for the SKU '{sku}' from the email body below:

        {email_body}

        Product Name:
        """
    elif criteria_description == "Sold Ship Now":
        prompt = f"""
        From the email below, find the exact product name located next to "Item:" for SKU '{sku}':

        {email_body}

        Product Name:
        """
    elif criteria_description == "Listing Created":
        prompt = f"""
        From the email below, find the exact product name located next to "Product Name" for SKU '{sku}':

        {email_body}

        Product Name:
        """
    else:
        prompt = f"""
        Extract the exact product name for SKU '{sku}' from the email below:

        {email_body}

        Product Name:
        """

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=25,
        temperature=0.0,
    )

    extracted_text = response.choices[0].message.content.strip()
    sku_name = extracted_text.split('\n')[0].strip()

    return sku_name
