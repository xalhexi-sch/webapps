from sqlalchemy import Column, Integer, String, Text, Numeric
from database import Base
 
class Product(Base):
    __tablename__ = "products"
 
    product_id          = Column(Integer,        primary_key=True, autoincrement=True)
    product_name        = Column(String(120),    nullable=False)
    product_description = Column(Text,           nullable=True)
    product_category    = Column(String(80),     nullable=True)
    product_price       = Column(Numeric(10, 2), nullable=False)
 
    # def to_dict(self):
    #     return {
    #         "product_id":          self.product_id,
    #         "product_name":        self.product_name,
    #         "product_description": self.product_description,
    #         "product_category":    self.product_category,
    #         "product_price":       str(self.product_price),
    #     }
 
    def __repr__(self):
        return f"<Product id={self.product_id} name={self.product_name!r}>"
