# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

import unittest


class  Test_generate_dictionaryTestCase(unittest.TestCase):
    def random_points(array_shape, num_points=None):
        points = []
        for each_dim in array_shape:
            points.append(np.random.random_integers(0, each_dim - 1, num_points))

        points = np.array(points).T

        return(points)
    
    def random_point_groups(array_shape, num_points=None, mean_group_size = 3.0):
        points = random_points(array_shape, num_points)

        groups = []
        points_grouped = 0

        while points_grouped < len(points):
            new_points_grouped = points_grouped + np.random.geometric(1.0 / float(mean_group_size))
            groups.append(points[points_grouped:new_points_grouped])
            points_grouped = new_points_grouped

        return(groups)
    
    def random_matrices_from_point_groups(array_shape, num_points = None, mean_group_size = 3.0):
        point_groups = random_point_groups(array_shape, num_points, mean_group_size)
        results = []

        for each_point_group in point_groups:
            results.append(random_matrix_from_points(array_shape, each_point_group))

        results = np.array(results)
        return(results)
    
    def expand_points_add_decay(array_shape, num_frames, num_points = None, mean_group_size = 3.0):
        matrices = random_matrices_from_point_groups(array_shape, num_points, mean_group_size)
        results = []

        for each_matrix in matrices:
            sigma = np.random.random()
            for each_frame_num in xrange(num_frames):
                rescale = float(num_frames - each_frame_num) / float(num_frames)
                each_matrix_convolved = scipy.ndimage.filters.gaussian_filter(rescale * each_matrix, sigma)
                results.append(each_matrix_convolved)

        results = np.array(results)

        return(results)
    
    #def setUp(self):
    #    self.foo = Test_generate_dictionary()
    #

    #def tearDown(self):
    #    self.foo.dispose()
    #    self.foo = None

    def test_test_generate_dictionary(self):
        #assert x != y;
        #self.assertEqual(x, y, "Msg");
        self.fail("TODO: Write test")

if __name__ == '__main__':
    unittest.main()

