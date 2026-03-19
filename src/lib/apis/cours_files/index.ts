import { TUTOR_API_BASE_URL } from '$lib/constants';

export interface CourseFileResponse {
    id: string;
    class_id: string;
    filename: string;
    file_path: string;
    file_type?: string;
    file_size?: number;
}


// ---------------- Upload File ----------------
export const uploadCourseFile = async (token: string,courseId: string, section: "courses" | "td" | "tp" | "exams", file: File): Promise<CourseFileResponse> => {
    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch(
        `${TUTOR_API_BASE_URL}/course-files/upload/${courseId}/${section}`,
        {
            method: "POST",
            headers: {
                Authorization: `Bearer ${token}`
            },
            body: formData
        }
    );

    if (!res.ok) {
        const error = await res.json();
        throw error.detail || "Failed to upload file";
    }

    return await res.json();
};


// ---------------- Get Files ----------------
export const getCourseFiles = async ( token: string, courseId: string): Promise<CourseFileResponse[]> => {
    const res = await fetch(`${TUTOR_API_BASE_URL}/course-files/course/${courseId}`, {
        method: "GET",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${token}`
        }
    });

    if (!res.ok) {
        const error = await res.json();
        throw error.detail || "Failed to fetch files";
    }

    return await res.json();
};


// ---------------- Delete File ----------------
export const deleteCourseFile = async (token: string,fileId: string) => {
    const res = await fetch(`${TUTOR_API_BASE_URL}/course-files/${fileId}`, {
        method: "DELETE",
        headers: {
            "Authorization": `Bearer ${token}`
        }
    });

    if (!res.ok) {
        const error = await res.json();
        throw error.detail || "Failed to delete file";
    }

    return await res.json();
};