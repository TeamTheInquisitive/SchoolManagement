import api from '../services/api';

/**
 * Fetch all pages of a paginated API and return combined results.
 * @param {string} url - API endpoint
 * @param {object} params - Query params (without page/page_size)
 * @param {number} pageSize - Page size per request (default 100)
 * @returns {Promise<Array>} All results combined
 */
export async function fetchAllPages(url, params = {}, pageSize = 100) {
  let allResults = [];
  let page = 1;
  let totalPages = 1;

  while (page <= totalPages) {
    const res = await api.get(url, { params: { ...params, page, page_size: pageSize } });
    const data = res.data;
    const results = data?.results || data?.students || data?.staff || data?.teachers || [];
    allResults = [...allResults, ...results];
    totalPages = data?.total_pages || 1;
    page++;
  }

  return allResults;
}
