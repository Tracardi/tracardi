#Core definitions

In order to understand how Tracardi CPD works you will need to learn the following definitions. 

##Source
In order to kick start your new project with Tracardi you must create a new source. That source will give you an identifier which when attached to your track calls will start collecting data about your users. There are two types of sources. The source that can emit events, e.g. web page. This type of source sends data to tracardi every time something happens. Other examples are SMS gateway, received email, payload from kafka queue.

The second type of source is the source that stores data, e.g. database. You have to query that source for data. It does not send data when something changed. 

Tracardi can access both types of sources. For example, someone visits your page (first source) tracardi receives an event with profile id then it queries the MySql database for additional data about the user (second source). 

Some sources may require user consent to collect data from this source. A web page requires consent from the user to collect and store his or her data. 

##Session
Session - an object that remembers the details of the connection with the client on the server for some time. A characteristic feature of the session is that the data assigned to it are usually temporary, volatile. 

##Event
Events represent something that is happening at a specific time (they are timestamped). They can be used to track visitor behaviour. Examples of events may include a click on a link on a web page, a login, a form submission, a page view or any other action that needs to be tracked, e.g. purchase order. Events can pass additional data such as user name, purchased item, viewed page, etc.

Web page events are raised when a javascript executes on a selected page. As a tracker is inserted on every page it can emit an event. Events and their types are configured by you. Also, you configure what data has to be sent with every event. 

Events can be stored inside Tracardi or just passed to workflow to be processed outside Tracardi.  

##Rule
Rules define which workflow is to be executed when an event comes to the system. 
Rules consist of a condition and workflow name. If a condition is met then the flow starts to run. The condition has two elements: event type and source.  If the event is of a certain type and comes from a given source then the defined workflow is executed. The source is optional in that equation so it can be set to any source. 

##Flows (short for workflows)

Flow is a graph of actions that will run when an event is matched with workflow. Actions may run one after another or in parallel. Workflow is represented as a graph of nodes and connections between them. Actions are assigned to nodes. Data flow from action to action is represented by connections between nodes. Actions may perform different tasks such as copying data from the event to profile, save profile, query for additional data, send to another system or emit another event. 


##Actions

Action is a single task in the workflow. Actions consist of input and output ports. Input ports are used to receive data. On the other hand, output ports send data via connection to another action. Action is basically a code in the system. Input ports are mapped to input parameters of a function in code when output ports are mapped to the return values. Tracardi can be extended by programmers who write code and map it with action, which later on is visible in the workflow editor as nodes.

##Profile

A profile is a set of data that represents user data. Profiles are updated based on incoming events and data from external systems. The profile has public and private data. Private data is usually sensitive data such as Name, surname, e-mail, age, total purchases. Public data is data e.g. on the segment to which the user belongs, last visit, number of visits, etc. 

The profile is updated by the workflow, and more precisely by the actions performed within the workflow. Data from profiles can be used for marketing campaigns, etc. 

##Segment 
The segment is the result of the segmentation of customer profiles. A segment can be described by a simple logical rule or by more complex AI models. The segment is part of the profile. A segment defined in the Tracardi system can be used in the segmentation workflow. The segment is represented by a simple sentence such as "Customers with high volume of purchases". 
  
