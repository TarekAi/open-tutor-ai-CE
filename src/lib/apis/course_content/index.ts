import { TUTOR_API_BASE_URL } from '$lib/constants';

export interface CourseCreateRequest {
    title: string;
    description?: string;
    type: string;
    classe_id: string;
}

export interface CourseResponse {
    id: string;
    title: string;
    description?: string;
    type: string;
    classe_id: string;
    user_id: string;
    created_at: string;
}


// ---------------- API FUNCTIONS ----------------


// Get courses of a class
export const getCoursesByClassId = async (token: string, classId: string): Promise<CourseResponse[]> => {

    let error = null;

    const res = await fetch(`${TUTOR_API_BASE_URL}/courses/classe/${classId}`, {
        method: 'GET',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        }
    })
    .then(async (res) => {
        if (!res.ok) throw await res.json();
        return res.json();
    })
    .catch((err) => {
        error = err.detail || "Failed to fetch courses";
        console.error("Error fetching courses:", err);
        return null;
    });

    if (error) throw error;

    return res;
};


// Create new course
export const createCourse = async (token: string, data: CourseCreateRequest): Promise<CourseResponse> => {

    let error = null;

    const res = await fetch(`${TUTOR_API_BASE_URL}/courses/create`, {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(data)
    })
    .then(async (res) => {
        if (!res.ok) throw await res.json();
        return res.json();
    })
    .catch((err) => {
        error = err.detail || "Failed to create course";
        console.error("Error creating course:", err);
        return null;
    });

    if (error) throw error;

    return res;
};


// Get single course
export const getCourseById = async (token: string, courseId: string): Promise<CourseResponse> => {

    const res = await fetch(`${TUTOR_API_BASE_URL}/courses/${courseId}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        }
    });

    if (!res.ok) throw await res.json();

    return await res.json();
};


// Update course
export const updateCourse = async (
    token: string,
    courseId: string,
    data: CourseCreateRequest
): Promise<CourseResponse> => {

    let error = null;

    const res = await fetch(`${TUTOR_API_BASE_URL}/courses/${courseId}`, {
        method: 'PATCH',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(data)
    })
    .then(async (res) => {
        if (!res.ok) throw await res.json();
        return res.json();
    })
    .catch((err) => {
        error = err.detail || "Failed to update course";
        console.error("Error updating course:", err);
        return null;
    });

    if (error) throw error;

    return res;
};


// Delete course
export const deleteCourse = async (token: string, courseId: string) => {

    let error = null;

    const res = await fetch(`${TUTOR_API_BASE_URL}/courses/${courseId}`, {
        method: 'DELETE',
        headers: {
            'Accept': 'application/json',
            'Authorization': `Bearer ${token}`
        }
    })
    .then(async (res) => {
        if (!res.ok) throw await res.json();
        return res.json();
    })
    .catch((err) => {
        error = err.detail || "Failed to delete course";
        console.error("Error deleting course:", err);
        return null;
    });

    if (error) throw error;

    return res;
};

// Get class content
export const getClassContent = async (token: string, classId: string) => {

	const res = await fetch(
		`${TUTOR_API_BASE_URL}/courses/classe/${classId}/content`,
		{
			method: 'GET',
			headers: {
				'Content-Type': 'application/json',
				authorization: `Bearer ${token}`
			}
		}
	);

	if (!res.ok) {
		throw new Error('Failed to fetch content');
	}

	return await res.json();
};