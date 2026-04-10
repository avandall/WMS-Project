"""
WMS-specific agent with database tools
"""
from typing import List, Dict, Any
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
import sqlalchemy
from sqlalchemy import text

from ..models.base import BaseAgent, AgentState
from ..config import settings


class WMSAgent(BaseAgent):
    """WMS agent with database query capabilities"""
    
    def __init__(self):
        # Initialize Groq LLM
        self.llm_config = settings.get_llm_config()
        self.llm = ChatGroq(**self.llm_config)
        
        # Setup tools
        self.tools = [self.query_inventory_db, self.query_order_status, self.query_location_info]
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        # Build workflow
        self.workflow = self._build_workflow()
        self.app = self.workflow.compile()
    
    @tool
    def query_inventory_db(self, sku_code: str):
        """
        Query inventory quantity and location from database by SKU code.
        Use this when user asks about stock levels, product locations, or inventory status.
        """
        try:
            engine = sqlalchemy.create_engine(settings.DB_CONNECTION_STRING)
            
            with engine.connect() as conn:
                query = text("""
                    SELECT quantity, location, product_name, last_updated 
                    FROM inventory 
                    WHERE sku = :sku
                """)
                result = conn.execute(query, {"sku": sku_code}).fetchone()
                
            if result:
                return f"""
                SKU {sku_code} - {result[2]}:
                - Quantity: {result[0]} units
                - Location: {result[1]}
                - Last Updated: {result[3]}
                """
            return f"No inventory information found for SKU {sku_code}."
            
        except Exception as e:
            return f"Error querying inventory: {str(e)}"
    
    @tool
    def query_order_status(self, order_id: str):
        """
        Query order status and details from database by order ID.
        Use this when user asks about order tracking, fulfillment status, or order details.
        """
        try:
            engine = sqlalchemy.create_engine(settings.DB_CONNECTION_STRING)
            
            with engine.connect() as conn:
                query = text("""
                    SELECT status, customer_name, order_date, total_amount, items
                    FROM orders 
                    WHERE order_id = :order_id
                """)
                result = conn.execute(query, {"order_id": order_id}).fetchone()
                
            if result:
                return f"""
                Order {order_id}:
                - Status: {result[0]}
                - Customer: {result[1]}
                - Order Date: {result[2]}
                - Total Amount: ${result[3]}
                - Items: {result[4]}
                """
            return f"No order found with ID {order_id}."
            
        except Exception as e:
            return f"Error querying order: {str(e)}"
    
    @tool
    def query_location_info(self, location_code: str):
        """
        Query warehouse location information and current contents.
        Use this when user asks about specific warehouse locations, zones, or areas.
        """
        try:
            engine = sqlalchemy.create_engine(settings.DB_CONNECTION_STRING)
            
            with engine.connect() as conn:
                query = text("""
                    SELECT zone, capacity, current_occupancy, location_type
                    FROM locations 
                    WHERE location_code = :location_code
                """)
                result = conn.execute(query, {"location_code": location_code}).fetchone()
                
            if result:
                return f"""
                Location {location_code}:
                - Zone: {result[0]}
                - Capacity: {result[1]} units
                - Current Occupancy: {result[2]} units
                - Type: {result[3]}
                """
            return f"No location found with code {location_code}."
            
        except Exception as e:
            return f"Error querying location: {str(e)}"
    
    def _build_workflow(self) -> StateGraph:
        """Build the agent workflow graph"""
        
        def call_model(state: AgentState):
            """Agent reasoning node"""
            messages = state["messages"]
            response = self.llm_with_tools.invoke(messages)
            return {"messages": [response]}
        
        def should_continue(state: AgentState):
            """Determine if tools are needed"""
            last_message = state["messages"][-1]
            if last_message.tool_calls:
                return "tools"
            return "__end__"
        
        # Create workflow
        workflow = StateGraph(AgentState)
        
        tool_node = ToolNode(self.tools)
        
        workflow.add_node("agent", call_model)
        workflow.add_node("tools", tool_node)
        
        workflow.set_entry_point("agent")
        workflow.add_conditional_edges("agent", should_continue)
        workflow.add_edge("tools", "agent")
        
        return workflow
    
    def process(self, question: str) -> str:
        """Process question using agent capabilities"""
        messages = [HumanMessage(content=question)]
        
        try:
            result = self.app.invoke({"messages": messages})
            final_message = result["messages"][-1]
            return final_message.content
        except Exception as e:
            return f"Error processing request: {str(e)}"
