import unittest
import ipdb
from experiment.models import Models, Parameters, make_dataframe, get_doc_metadata, get_val_from_df, bin_dataframe, filter_results_with_binary_dataframe
from facets.query import get_facets_for_q
from dateutil.parser import parse

def mock_post():
    params = Parameters()
    params.q = "Mitch Landrieu"
    params.f = "Department of Justice"

    results = Models.get_results(params)

    aliases = [] # cache[params.q + "##" + params.detail]
    
    metadata = [get_doc_metadata(r) for r in results]

    q_pubdates = [parse(h["pubdate"]) for h in metadata]

    # note no aliases
    df = make_dataframe(params, [params.f], results, q_pubdates, aliases)

    results = filter_results_with_binary_dataframe(results, params.f, df)

    doc_list = Models.get_doclist(results, params, aliases=aliases)

    return doc_list


class GenericTestCase(unittest.TestCase):

    def test_binning(self):
        '''
        does pandas binning == dumb counting via loop? it should
        '''
        params = Parameters()
        params.q = "Mitch Landrieu"
        results = Models.get_results(params)
        aliases = []
        metadata = [get_doc_metadata(r) for r in results]
        q_pubdates = [parse(h["pubdate"]) for h in metadata]
        binned_facets = get_facets_for_q(params.q, results, 9)
        
        # df is a binary matrix that has a 1 or 0 depending on if a facet shows up in df
        df = make_dataframe(params, binned_facets['g'], results, q_pubdates, aliases)
        counter_val = 0 
        for r in df.iterrows():
            if r[1]["pd"].month == 10 and r[1]["Department of Justice"] == 1 and r[1]["pd"].year == 2011: # r is a series
                counter_val += 1
        
        df = bin_dataframe(df, "month")

        df_val = int(get_val_from_df("Department of Justice", "2011-10", df))

        # pandas binning == dumb counting via loop? it should
        self.assertEqual(df_val, counter_val)


    def test_post(self):
        '''
        is the doc list the same as the dataframe?
        '''
        doclist = mock_post()
        doj_2011_10_post = len([parse(i["pubdate"]) for i in doclist if parse(i["pubdate"]).year == 2011 and parse(i["pubdate"]).month == 10])

        #### post_val is how many DOJ docs you get on post for q="Mitch Landrieu", f="Department of Justice"

        params = Parameters()

        params.q = "Mitch Landrieu"

        results = Models.get_results(params)

        aliases = [] # cache[params.q + "##" + params.detail]
        
        metadata = [get_doc_metadata(r) for r in results]

        q_pubdates = [parse(h["pubdate"]) for h in metadata]

        binned_facets = get_facets_for_q(params.q, results, 9)
        # note no aliases
        df = make_dataframe(params, binned_facets["g"], results, q_pubdates, aliases)

        counter_val = 0 
        for r in df.iterrows():
            if r[1]["pd"].month == 10 and r[1]["Department of Justice"] == 1 and r[1]["pd"].year == 2011: # r is a series
                counter_val += 1
        
        df = bin_dataframe(df, "month")

        ## df val is how many DOJ counts you get in initial query
        df_val = int(get_val_from_df("Department of Justice", "2011-10", df))

        self.assertEqual(df_val, doj_2011_10_post)

if __name__ == '__main__':
    unittest.main()
