// Historical classroom examples transcribed or abbreviated from the reference images.
const examples = [
 ["MCL_364427","Repair of boundary wall and workshop shed","Mahanadi Coalfields Limited","Boundary wall",93],
 ["AAI_287284","Annual civil repair and maintenance of operational building","Airports Authority of India","Civil repair",89],
 ["ISMU_921565","Renovation of five toilets and replacement of damaged fittings","IIT (ISM) Dhanbad","Renovation",90],
 ["ISMU_921540","Mess storeroom renovation and Kota stone flooring","IIT (ISM) Dhanbad","Renovation",80],
 ["IITR_921589","Whitewashing and painting residences, hostel and department","IIT Roorkee","Civil repair",73],
 ["IITR_921599","Residential maintenance in Zone B","IIT Roorkee","Civil repair",85],
 ["ISMU_921571","External repairs to Environmental Science building","IIT (ISM) Dhanbad","Civil repair",78],
 ["NTPC_118964","Construction of culvert and associated repair works","NTPC Limited","Civil works",55],
 ["NTPC_118950","Construction of box culverts at identified locations","NTPC Limited","Civil works",75],
 ["NTPC_118955","Stainless steel railing and seating for musical fountain","NTPC Limited","Civil works",86],
 ["NTPC_118952","Construction of two classrooms for DAV school","NTPC Limited","Building construction",85],
 ["MES_783785","Repair of internal and external finishes and flooring","Military Engineer Services","Civil repair",80],
 ["STATE_TN_3DCP_003","3DCP prefabricated modular infrastructure housing project","Tamil Nadu Housing Board","Modular housing",75]
].map(([id,title,org,category,score],i)=>({id:"example-"+id,ref:id,title,org,category,score,source:"Screenshot example",state:i===12?"Tamil Nadu":null,budget:i===12?"₹85 lakh":null,explanation:"Historical example with the reference image’s displayed score. Current availability has not been checked."}));
