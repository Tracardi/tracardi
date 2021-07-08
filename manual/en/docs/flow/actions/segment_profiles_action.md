# Segment Profile Action

After the flow is finished a procedure of Customer Segmentation is run. 

Segmentation is the practice of dividing a customers into groups that reflect similarity among them. 

To do that Tracardi uses conditions that define how customer data gets assigned to the segment group.  
This is defined outside ot the workflow but workflow must trigger this procedure. There is an exception to this rule. 
If profile is updated it will automatically trigger user segmentation. No need to do it manually in the workflow.

If for some reason you want to trigger segmentation manually connect this node in the workflow.   

## Configuration

This node needs no configuration. It does not require any input data and does not return data.

## Side effect

Segmentation does not have side effects.