#!/usr/bin/env python
# coding: utf-8

# In[27]:


import numpy as np
import pandas as pd
import ast
import plotly.express as px
from plotly import graph_objects as go
df = pd.read_csv('flipkart_com-ecommerce_sample.csv')


# In[28]:


df.isnull().sum()


# In[29]:


df["retail_price"].fillna(df["retail_price"].median(),inplace=True)
df["discounted_price"].fillna(df["discounted_price"].median(),inplace=True)


# In[30]:


x=df['retail_price']-df['discounted_price']
y=(x/df['retail_price'])*100
df['discount_percentage']=y


# In[31]:


df['timestamp']=pd.to_datetime(df['crawl_timestamp'])  #converting into datetime to extract date and time easily
df['Time']=df['timestamp'].apply(lambda x : x.time)  #extracting time
df['date']=df['timestamp'].apply(lambda x : x.date)  #extracting date
df.drop(['crawl_timestamp'], axis = 1,inplace=True)  #dropping the column
df['main_category']=df['product_category_tree'].apply(lambda x :x.split('>>')[0][2:len(x.split('>>')[0])-1])  #new column using product_category_tree


# In[32]:


# Top 10 main products being purchased

n = 10
top_products=pd.DataFrame(df['main_category'].value_counts()  [:n]).reset_index()
top_products.rename(columns = {'index':'Top_Products','main_category':'Total_Count'}, inplace = True)

#Top 10 main brands being purchased

n = 10
top_brands=pd.DataFrame(df['brand'].value_counts()[:n]).reset_index()
top_brands.rename(columns = {'index':'Top_Brands','brand':'Total_Count'}, inplace = True)


# In[33]:


from plotly.subplots import make_subplots #plotly library to create subplots

label1 = top_products['Top_Products']
value1=top_products['Total_Count']
label2=top_brands['Top_Brands']
value2=top_brands['Total_Count']

# Create subplots

fig_both = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}]])
fig_both.add_trace(go.Pie(labels=label1, values=value1, name="Top Products",pull=[0.3, 0, 0, 0]),
              1, 1)
fig_both.add_trace(go.Pie(labels=label2, values=value2, name="Top Brands",pull=[0.3, 0, 0, 0]),
              1, 2)

# Use `hole` to create a donut-like pie chart

fig_both.update_traces(hole=.4, hoverinfo="label+percent+name")
#fig_both.update_traces(hoverinfo="label+percent+name")

fig_both.update_layout(
    title_text="Top products and brands distribution",
    #Add annotations in the center of the donut pies
    
    annotations=[dict(text='Product', x=0.18, y=0.5, font_size=20, showarrow=False),
                 dict(text='Brand', x=0.82, y=0.5, font_size=20, showarrow=False)])
                 
fig_both.show()



# In[34]:


df_discount=df.query('discount_percentage > 90')  #targeting brands giving high discounts
df_discount=df_discount.dropna() #dropping rows with NA values
df_discount["brand"].replace('FashBlush','Fash Blush',inplace=True) #handling spelling errors
max_discount=pd.DataFrame(df_discount.groupby('brand')[['discount_percentage']].mean().sort_values(by=['discount_percentage'],ascending=False).reset_index())  #creating a dataframe


# In[35]:


px.bar(max_discount, x= 'brand', y='discount_percentage',color='brand',color_discrete_sequence=px.colors.qualitative.Dark2)  #plotting a bar graph


# In[36]:


df_customer=df.groupby("uniq_id")[["discounted_price"]].sum().sort_values(by=['discounted_price'],ascending=[False]).reset_index()

#Top 20 customers spending the most
list1=df_customer[:20]

#plotting a bar graph
px.bar(list1, x= 'uniq_id', y="discounted_price",color='discounted_price',color_continuous_scale=px.colors.diverging.BrBG)


# In[37]:


total_prod=len(df['pid'])  #total products using pid variable
total_ratings=len(df[df['product_rating']!='No rating available']) #total rated products
top_ratings=len(df[df['product_rating']=='5']) #5 star rated products
df_funnel_1 = dict(
    number=[total_prod,total_ratings,top_ratings],
    stage=["Total Products","Products with ratings","Products with 5 star rating"])
funnel_1_fig = px.funnel(df_funnel_1, x='number', y='stage')
funnel_1_fig.show()


# In[48]:


#5 star products/brands
rating_5=pd.DataFrame(df.loc[df['product_rating'] == '5'])
top_product_type=rating_5['main_category'].value_counts() #top products
top_brand_type=rating_5['brand'].value_counts()  #top brands

#top 5 products
df_top_product=pd.DataFrame(top_product_type[:5].reset_index()) #first 5
df_top_product.rename(columns = {'index':'top_prod'}, inplace = True) 
df_top_product.drop('main_category', inplace=True, axis=1)

#top 5 brands
df_top_brand=pd.DataFrame(top_brand_type[:5].reset_index())
df_top_brand.rename(columns = {'index':'top_brands'}, inplace = True)
df_top_brand.drop('brand', inplace=True, axis=1)
df_top_brand.head()




# In[43]:


df.drop(df.index[df['product_rating'] == 'No rating available'], inplace = True) 
ratings=pd.DataFrame(df['product_rating'].value_counts().reset_index())
ratings['index'] = ratings['index'].astype(float)
ratings.head().sort_values(by=['index'],ascending=[False])
ratings.rename(columns = {'index':'Ratings','product_rating':'Counts'}, inplace = True)

# plotting the result
data=ratings
x=ratings['Ratings']
y=ratings['Counts']
figdot2 = go.Figure()
figdot2.add_trace(go.Scatter(
    x=x,
    y=y,
    marker=dict(color="crimson", size=12),
    mode="markers",
    name="ratings",
))

figdot2.update_layout(title="Ratings v/s Count",
                  xaxis_title="Ratings",
                  yaxis_title="Count",
                     )

figdot2.update_xaxes(showline=True, linewidth=1, linecolor='black', mirror=True)
figdot2.update_yaxes(showline=True, linewidth=1, linecolor='black', mirror=True)
figdot2.show()


# # Is there any trend associated with the retail price and discount price over the months?

# In[45]:


df_date_retail = pd.DataFrame(df.groupby("date")[["retail_price"]].mean().reset_index())
df_date_discount = pd.DataFrame(df.groupby("date")[["discounted_price"]].mean().reset_index())
df_date_price=pd.concat([df_date_retail,df_date_discount],axis=1)
df_date_price = df_date_price.loc[:,~df_date_price.columns.duplicated()] #remove duplicate columns

#Plot
x=df_date_price['date']
y1=df_date_price['retail_price']
y2=df_date_price['discounted_price']

fig_area2 = go.Figure()
fig_area2.add_trace(go.Scatter(x=x, y=y1, fill='tozeroy',name='retail price',
                               line=dict(width=0.5, color='crimson'))) # fill down to xaxis
fig_area2.add_trace(go.Scatter(x=x, y=y2, fill='tozeroy',name='discount price',
                               line=dict(width=0.5, color='darkslategray')
                              )) # fill to trace0 y

fig_area2.update_layout(
    xaxis_title="Dates",
    yaxis_title="Price (in 1000s)",
    plot_bgcolor='white'
)
fig_area2.update_xaxes(showline=True, linewidth=1, linecolor='black', mirror=True)
fig_area2.update_yaxes(showline=True, linewidth=1, linecolor='black', mirror=True)
fig_area2.show()


# # When are customers the most active during the day?

# In[46]:


scat2 = px.scatter(x=df['Time'].sort_values(ascending=True), y=df['product_url'])
scat2.update_layout(
    title_text='No. of clicks vs time', # title of plot
    xaxis_title_text='Time', # xaxis label
    yaxis_title_text='No. of Clicks', # yaxis label

)
#scat.update_xaxes(showticklabels=False)
scat2.update_yaxes(showticklabels=False)
scat2.update_xaxes(showline=True, linewidth=1, linecolor='black', mirror=True)
scat2.update_yaxes(showline=True, linewidth=1, linecolor='black', mirror=True)
scat2.show()




