"""Build a standalone, rule-based product finder; AI is used by the host for design work."""
import argparse
import json
from urllib.parse import urlsplit
from skill_io import index, number, read_json, rows, save


HTML = '''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Product finder prototype</title><style>
body{font:16px/1.6 system-ui,sans-serif;background:#f2f7f6;color:#18313a;margin:0}main{max-width:850px;margin:45px auto;padding:25px}h1{font-size:2.5rem;line-height:1.1}label{display:block;margin:20px 0}select,button{font:inherit;padding:10px;border:1px solid #8ba8ae;border-radius:6px}select{display:block;min-width:240px}button{background:#096e70;color:white;cursor:pointer}article{padding:18px;background:white;border:1px solid #d4e2e3;border-radius:9px;margin:15px 0}small{display:block;color:#536970}a{color:#096e70}#results:focus{outline:2px solid #096e70}
</style></head><body><main><small>Editable local prototype - supplied catalog snapshot</small><h1 id="heading"></h1><p>Choose what matters. Matching uses the explicit rules in this file.</p><form id="quiz"></form><h2>Matching products</h2><div id="results" tabindex="-1" aria-live="polite"></div></main>
<script type="application/json" id="finder-data">__DATA__</script><script>
const config=JSON.parse(document.getElementById('finder-data').textContent);
document.getElementById('heading').textContent=config.title;
const form=document.getElementById('quiz');
const selections=new Map();
for(const q of config.questions){const label=document.createElement('label');label.textContent=q.label;const select=document.createElement('select');select.name=q.id;selections.set(q.id,select);const empty=document.createElement('option');empty.value='';empty.textContent='Any';select.append(empty);for(let i=0;i<q.options.length;i++){const option=document.createElement('option');option.value=String(i);option.textContent=q.options[i].label;select.append(option)}label.append(select);form.append(label)}
const button=document.createElement('button');button.type='submit';button.textContent='Find products';form.append(button);
function accepts(product,rule){return Object.entries(rule).every(([key,value])=>key==='max_price'?Number(product.price)<=Number(value):product.attributes[key]===value)}
function show(event){if(event)event.preventDefault();const rules=config.questions.flatMap(q=>{const choice=selections.get(q.id).value;return choice===''?[]:[q.options[Number(choice)].where]});const products=config.products.filter(p=>p.available && rules.every(rule=>accepts(p,rule)));const results=document.getElementById('results');results.replaceChildren();if(!products.length){results.textContent='No matching products in this catalog. Change your choices or ask the store for help.'}for(const p of products){const card=document.createElement('article');const h=document.createElement('h3');h.textContent=p.name;card.append(h);const price=document.createElement('p');price.textContent=p.currency+' '+p.price;card.append(price);const why=document.createElement('small');why.textContent='Matches the selected catalog constraints. Availability is a supplied snapshot.';card.append(why);if(p.url){const link=document.createElement('a');link.href=p.url;link.rel='noopener noreferrer';link.textContent='View product';card.append(link)}results.append(card)}if(event)results.focus()}
form.addEventListener('submit',show);show();
</script></body></html>'''


def process(data):
    products = rows(data.get("products", []), "products")
    index(products)
    currencies = set()
    for product in products:
        if not isinstance(product.get("name"), str) or not isinstance(product.get("attributes"), dict):
            raise ValueError("Every product needs a name and attributes object")
        if not isinstance(product.get("available"), bool):
            raise ValueError("available must be a boolean")
        product["price"] = str(number(product.get("price"), "price", 0))
        currencies.add(product.get("currency"))
        url = product.get("url", "")
        if url:
            parsed = urlsplit(url)
            if not (parsed.scheme == "https" and parsed.netloc) and not (url.startswith("/") and not url.startswith("//")):
                raise ValueError("Product links must be https URLs or root-relative paths")
    if len(currencies) != 1 or not all(isinstance(c, str) and len(c) == 3 for c in currencies):
        raise ValueError("Use one explicit three-letter currency")
    questions = rows(data.get("questions", []), "questions")
    index(questions)
    known = {k for p in products for k in p["attributes"]}
    for question in questions:
        if not isinstance(question.get("label"), str):
            raise ValueError("Question needs a label")
        for option in rows(question.get("options", []), "options"):
            if not isinstance(option.get("label"), str) or not isinstance(option.get("where"), dict):
                raise ValueError("Option needs a label and where object")
            for key, value in option["where"].items():
                if key == "max_price":
                    number(value, "max_price", 0)
                elif key not in known:
                    raise ValueError(f"Unknown attribute constraint: {key}")
    payload = {"title": str(data.get("title", "Find your product")), "products": products, "questions": questions}
    encoded = json.dumps(payload, ensure_ascii=True, allow_nan=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    return {"html": HTML.replace("__DATA__", encoded), "product_count": len(products),
            "runtime": "local_rule_based", "live_inventory": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", help="Optional JSON result")
    parser.add_argument("--html-output", help="Optional standalone HTML file")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    try:
        data = read_json(args.input)
        if not isinstance(data, dict):
            raise ValueError("Input must be an object")
        result = process(data)
        if args.output:
            save(args.output, json.dumps(result, indent=2) + "\n", args.overwrite)
        if args.html_output:
            save(args.html_output, result["html"], args.overwrite)
        if not args.output:
            print(json.dumps({k:v for k,v in result.items() if k != "html"} if args.html_output else result, indent=2))
    except (OSError, ValueError, TypeError, KeyError) as exc:
        parser.exit(2, f"Input/output error: {exc}\n")


if __name__ == "__main__":
    main()
