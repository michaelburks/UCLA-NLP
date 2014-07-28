""" cfg2e
"""

sample0 = [
    ['she','will','put','it','there','then'],
    ['she','will','put','this','one','there','then'],
    ['she','will','put','it','on','this','one','then'],
    ['this','one','will','put','it','there','then'],
    ['this','girl','in','the','red','coat','will','put','a','picture','of','Bill','on','your','desk','before','tomorrow'],
    ['she','will','put','a','picture','of','Bill','on','your','desk','before','tomorrow'],
    ['this','girl','in','the','red','coat','will','put','it','on','your','desk','before','tomorrow'],
    ['this','girl','in','the','red','coat','will','put','a','picture','of','Bill','there','before','tomorrow'],
    ['this','one','will','put','a','picture','of','Bill','on','your','desk','before','tomorrow'],
    ['this','girl','in','the','red','coat','will','put','a','picture','of','Bill','on','it','before','tomorrow'],
    ['this','girl','in','the','red','one','will','put','a','picture','of','Bill','on','your','desk','before','tomorrow']
    ]
target0 = ([], # P0
           [], # P1
           [('S','DP','TP'), # P2
            ('DP','D','NP'),
            ('DP','D','N'),
            ('NP','N','PP'),
            ('PP','P','DP'),
            ('N','A','N'),
            ('NP','A','NP'),
            ('TP','T','VP'),
            ('VP','VP','PP'),
            ('VP','V','V2P'),
            ('V2P','DP','PP')], 
            [('DP','she'), # PL
            ('DP','it'),
            ('DP','Bill'),
            ('DP','tomorrow'),
            ('D','this'), 
            ('D','the'),
            ('D','a'),
            ('D','your'),
            ('A','red'),
            ('NP','one'),
            ('N','girl'),
            ('N','picture'),
            ('N','coat'),
            ('N','desk'),
            ('P','in'),
            ('P','of'),
            ('P','on'),
            ('P','before'),
            ('T','will'),
            ('V','put'),
            ('D','a'),
            ('P','of'),
            ('PP','there'),
            ('PP','then'),]
        )
start0 = 'S'