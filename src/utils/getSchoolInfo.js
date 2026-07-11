/**
 * Convert school profile data into the format expected by export utilities.
 * @param {object} schoolProfile - Data from useSchoolProfile()
 * @returns {object|null} School info object for export headers
 */
export function getSchoolInfo(schoolProfile) {
  if (!schoolProfile?.school_name) return null;
  return {
    name: schoolProfile.school_name,
    code: schoolProfile.school_code || '',
    address: schoolProfile.address || '',
    phone: schoolProfile.phone || '',
    email: schoolProfile.email || '',
    board: schoolProfile.board || '',
  };
}
