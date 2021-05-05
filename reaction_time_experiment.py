#!/usr/bin/env python
# coding: utf-8

# In[210]:


import seaborn as sns
import csv
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from scipy.stats import ttest_ind
import math

cols = ['ID', 'Condition', 'Repetition', 'Color', 'HEX', 'Delaytime(ms)', 'PressedKey', 'Correct?', 'Timestamp(Teststart)', 'start', 'end']
df = pd.read_csv('results.csv', names=cols, sep=",")
pd.set_option('display.max_rows', df.shape[0]+1)
#df.fillna(0, inplace=True)

df.drop(df.index[(df["ID"] == "567587")],inplace=True)

df


# In[255]:


df_easy = df[df['Condition'] == 'easy']

df_hard = df[df['Condition'] == 'hard']

begin_easy = df_easy.start.tolist()
end_easy = df_easy.end.tolist()


for i in range(len(begin_easy)):
    begin_easy[i] = float(begin_easy[i])
    
for i in range(len(begin_hard)):
    begin_hard[i] = float(begin_hard[i])


for i in range(len(end_easy)):
        end_easy[i] = float(end_easy[i])
            
end_easy[4] = 1620153646.665695
end_easy[11] = 1620153866.8927402
end_easy[15] = 1620153882.61128
end_easy[36] = 1620154199.2810023
end_easy[41] = 1620154293.9195926
end_easy[50] = 1620154422.5335824
end_easy[53] = 1620154428.638731            
            

begin_hard = df_hard.start.tolist()
end_hard = df_hard.end.tolist()

for i in range(len(end_hard)):
        end_hard[i] = float(end_hard[i])

end_hard[1] = 1620153679.9266028
end_hard[4] =1620153692.322446
end_hard[14] =1620153940.281751
end_hard[20] =1620154057.615727
end_hard[35] =1620154248.2309997
end_hard[39] =1620154288.5089946
end_hard[45] =1620154378.68068
end_hard[49] =1620154421.6341023
end_hard[58] =1620154528.0092819
        
begin_hard
    


# In[257]:


final_list_easy = []
final_list_hard = []

for i in range(len(end_easy)):
    value = end_easy[i]-begin_easy[i]
    final_list_easy.append(value)

for i in range(len(end_hard)):
    val = end_hard[i]-float(begin_hard[i])
    final_list_hard.append(val)
    
final_list_hard


# In[258]:


df_easy = pd.DataFrame(final_list_easy)
df_easy.describe()


# In[259]:


sns.boxplot(final_list_easy)


# In[260]:


df_hard = pd.DataFrame(final_list_hard)
df_hard.describe()


# In[263]:


sns.boxplot(final_list_hard)


# In[264]:


sns.scatterplot(final_list_easy)


# In[265]:


sns.scatterplot(final_list_hard)


# In[266]:


ttest_ind(final_list_easy, final_list_hard)


# In[ ]:




