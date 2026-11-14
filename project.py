{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "id": "bcf3bc02",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "\n",
      "\u001b[1m[\u001b[0m\u001b[34;49mnotice\u001b[0m\u001b[1;39;49m]\u001b[0m\u001b[39;49m A new release of pip is available: \u001b[0m\u001b[31;49m26.2.2\u001b[0m\u001b[39;49m -> \u001b[0m\u001b[32;49m26.3\u001b[0m\n",
      "\u001b[1m[\u001b[0m\u001b[34;49mnotice\u001b[0m\u001b[1;39;49m]\u001b[0m\u001b[39;49m To update, run: \u001b[0m\u001b[32;49mpython3 -m pip install --upgrade pip\u001b[0m\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "/usr/local/python/3.14.2/lib/python3.14/site-packages/tqdm/auto.py:21: TqdmWarning: IProgress not found. Please update jupyter and ipywidgets. See https://ipywidgets.readthedocs.io/en/stable/user_install.html\n",
      "  from .autonotebook import tqdm as notebook_tqdm\n",
      "/tmp/ipykernel_8013/3575582401.py:5: DeprecationWarning: Use dataset_load() instead of load_dataset(). load_dataset() will be removed in a future version.\n",
      "  df = kagglehub.load_dataset(\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Downloading to /home/codespace/.cache/kagglehub/datasets/gpreda/reddit-wallstreetsbets-posts/versions/106/reddit_wsb.csv...\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "100%|██████████| 16.5M/16.5M [00:00<00:00, 40.3MB/s]"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Extracting zip of reddit_wsb.csv...\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "(53187, 8)\n"
     ]
    },
    {
     "data": {
      "text/html": [
       "<div>\n",
       "<style scoped>\n",
       "    .dataframe tbody tr th:only-of-type {\n",
       "        vertical-align: middle;\n",
       "    }\n",
       "\n",
       "    .dataframe tbody tr th {\n",
       "        vertical-align: top;\n",
       "    }\n",
       "\n",
       "    .dataframe thead th {\n",
       "        text-align: right;\n",
       "    }\n",
       "</style>\n",
       "<table border=\"1\" class=\"dataframe\">\n",
       "  <thead>\n",
       "    <tr style=\"text-align: right;\">\n",
       "      <th></th>\n",
       "      <th>title</th>\n",
       "      <th>score</th>\n",
       "      <th>id</th>\n",
       "      <th>url</th>\n",
       "      <th>comms_num</th>\n",
       "      <th>created</th>\n",
       "      <th>body</th>\n",
       "      <th>timestamp</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>0</th>\n",
       "      <td>It's not about the money, it's about sending a...</td>\n",
       "      <td>55</td>\n",
       "      <td>l6ulcx</td>\n",
       "      <td>https://v.redd.it/6j75regs72e61</td>\n",
       "      <td>6</td>\n",
       "      <td>1.611863e+09</td>\n",
       "      <td>NaN</td>\n",
       "      <td>2021-01-28 21:37:41</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>1</th>\n",
       "      <td>Math Professor Scott Steiner says the numbers ...</td>\n",
       "      <td>110</td>\n",
       "      <td>l6uibd</td>\n",
       "      <td>https://v.redd.it/ah50lyny62e61</td>\n",
       "      <td>23</td>\n",
       "      <td>1.611862e+09</td>\n",
       "      <td>NaN</td>\n",
       "      <td>2021-01-28 21:32:10</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2</th>\n",
       "      <td>Exit the system</td>\n",
       "      <td>0</td>\n",
       "      <td>l6uhhn</td>\n",
       "      <td>https://www.reddit.com/r/wallstreetbets/commen...</td>\n",
       "      <td>47</td>\n",
       "      <td>1.611862e+09</td>\n",
       "      <td>The CEO of NASDAQ pushed to halt trading “to g...</td>\n",
       "      <td>2021-01-28 21:30:35</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>3</th>\n",
       "      <td>NEW SEC FILING FOR GME! CAN SOMEONE LESS RETAR...</td>\n",
       "      <td>29</td>\n",
       "      <td>l6ugk6</td>\n",
       "      <td>https://sec.report/Document/0001193125-21-019848/</td>\n",
       "      <td>74</td>\n",
       "      <td>1.611862e+09</td>\n",
       "      <td>NaN</td>\n",
       "      <td>2021-01-28 21:28:57</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>4</th>\n",
       "      <td>Not to distract from GME, just thought our AMC...</td>\n",
       "      <td>71</td>\n",
       "      <td>l6ufgy</td>\n",
       "      <td>https://i.redd.it/4h2sukb662e61.jpg</td>\n",
       "      <td>156</td>\n",
       "      <td>1.611862e+09</td>\n",
       "      <td>NaN</td>\n",
       "      <td>2021-01-28 21:26:56</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "                                               title  score      id  \\\n",
       "0  It's not about the money, it's about sending a...     55  l6ulcx   \n",
       "1  Math Professor Scott Steiner says the numbers ...    110  l6uibd   \n",
       "2                                    Exit the system      0  l6uhhn   \n",
       "3  NEW SEC FILING FOR GME! CAN SOMEONE LESS RETAR...     29  l6ugk6   \n",
       "4  Not to distract from GME, just thought our AMC...     71  l6ufgy   \n",
       "\n",
       "                                                 url  comms_num       created  \\\n",
       "0                    https://v.redd.it/6j75regs72e61          6  1.611863e+09   \n",
       "1                    https://v.redd.it/ah50lyny62e61         23  1.611862e+09   \n",
       "2  https://www.reddit.com/r/wallstreetbets/commen...         47  1.611862e+09   \n",
       "3  https://sec.report/Document/0001193125-21-019848/         74  1.611862e+09   \n",
       "4                https://i.redd.it/4h2sukb662e61.jpg        156  1.611862e+09   \n",
       "\n",
       "                                                body            timestamp  \n",
       "0                                                NaN  2021-01-28 21:37:41  \n",
       "1                                                NaN  2021-01-28 21:32:10  \n",
       "2  The CEO of NASDAQ pushed to halt trading “to g...  2021-01-28 21:30:35  \n",
       "3                                                NaN  2021-01-28 21:28:57  \n",
       "4                                                NaN  2021-01-28 21:26:56  "
      ]
     },
     "execution_count": 1,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "!pip install -q \"kagglehub [pandas-datasets]\"\n",
    "import kagglehub\n",
    "from kagglehub import KaggleDatasetAdapter\n",
    "\n",
    "df = kagglehub.load_dataset(\n",
    "    KaggleDatasetAdapter. PANDAS,\n",
    "    \"gpreda/reddit-wallstreetsbets-posts\",\n",
    "    \"reddit_wsb.csv\",\n",
    ")\n",
    "\n",
    "print(df.shape)\n",
    "df.head()"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.14.2"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
