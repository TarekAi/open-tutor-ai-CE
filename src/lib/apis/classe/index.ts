import { TUTOR_API_BASE_URL } from '$lib/constants';

// -------------------- Types --------------------
export interface ClasseCreateRequest {
    name: string;
    course?: string;
}
export interface ClasseResponse {
    id: string;
    name: string;
    course?: string;
    user_id: string;
    student_count: number;
    created_at: string;
    updated_at?: string;
}
export interface AddStudentRequest {
    name: string;
    email: string;
    classId: string;
}
export interface EnrollmentResponse {
    id: string;
    points: number;
    user: {
        name: string;
        profile_image_url?: string;
        email: string;
    };
    created_at: string;
}

// ======= API Functions =======
// ----- get all classes of the teacher -----
export const getMyClasses = async (token: string): Promise<ClasseResponse[]> => {
    let error = null;
    const res = await fetch(`${TUTOR_API_BASE_URL}/classe/all`, {
        method: 'GET',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'authorization': `Bearer ${token}`
        }
    })
    .then(async (res) => {
        if (!res.ok) throw await res.json();
        return res.json();
    })
    .catch((err) => {
        error = err.detail || "Failed to fetch classes";
        console.error('Error fetching classes:', err);
        return null;
    });

    if (error) throw error;
    return res;
};

// ----- get class by id -----
export const getClassById = async (token: string, classId: string): Promise<ClasseResponse> => {
    let error = null;

    const res = await fetch(`${TUTOR_API_BASE_URL}/classe/${classId}`, {
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
        error = err.detail || "Failed to fetch class";
        console.error('Error fetching class:', err);
        return null;
    });

    if (error) throw error;
    return res;
};

// ---------------- create New Class ----------------
export const createNewClass = async (token: string, data: ClasseCreateRequest): Promise<ClasseResponse> => {
    let error = null;

    const res = await fetch(`${TUTOR_API_BASE_URL}/classe/create`, {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'authorization': `Bearer ${token}`
        },
        body: JSON.stringify(data)
    })
    .then(async (res) => {
        if (!res.ok) throw await res.json();
        return res.json();
    })
    .catch((err) => {
        error = err.detail || "Failed to create class";
        console.error('Error creating class:', err);
        return null;
    });

    if (error) throw error;
    return res;
};

// ---------------- Update Class ----------------
export const updateClass = async (token: string, classId: string, data: ClasseCreateRequest): Promise<ClasseResponse> => {
    let error = null;
    const res = await fetch(`${TUTOR_API_BASE_URL}/classe/${classId}`, {
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
        error = err.detail || "Failed to update class";
        console.error('Error updating class:', err);
        return null;
    });

    if (error) throw error;
    return res;
};

// ---------------- Delete Class ----------------
export const deleteClassById = async (token: string, classId: string) => {
    let error = null;

    const res = await fetch(`${TUTOR_API_BASE_URL}/classe/${classId}`, {
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
        error = err.detail || "Failed to delete class";
        console.error('Error deleting class:', err);
        return null;
    });

    if (error) throw error;
    return res;
};

// ================= Enrollment Management =================
// ---------------- Add Student to Class ----------------
export const addStudentToClass = async (token: string, data: AddStudentRequest) => {
    const res = await fetch(`${TUTOR_API_BASE_URL}/classe/add-student`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(data)
    });

    if (!res.ok) {
        const error = await res.json();
        throw error.detail || "Failed to add student";
    }
    return res.json();
};

// ------ get students by class id ------------
export const getStudentsByClassId = async (token: string, classId: string) => {
    const res = await fetch(`${TUTOR_API_BASE_URL}/classe/${classId}/students`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        }
    });
    
    if (!res.ok) throw await res.json();
    return await res.json();
};

// ---------------- Update Student Grade ----------------
export const updateStudentGrade = async (token: string, classId: string, userId: string, data: { grade: number, notes: string }) => {
    const res = await fetch(`${TUTOR_API_BASE_URL}/classe/${classId}/students/${userId}/grade`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(data)
    });
    if (!res.ok) throw await res.json();
    return res.json();
};

// ---------------- Remove Student from Class ----------------






// ================= Dashboard Statistics =================
// ----------------- Get Teacher Statistics ----------------
export const getTeacherStats = async (token: string, classId?: string) => {
    // Ila kan classId khawi, ghadi njibo stats dial kolchi
    const url = classId 
        ? `${TUTOR_API_BASE_URL}/classe/teacher/statistics?classe_id=${classId}`
        : `${TUTOR_API_BASE_URL}/classe/teacher/statistics`;

    const res = await fetch(url, {
        method: 'GET',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        }
    });

    if (!res.ok) {
        const error = await res.json();
        throw error.detail || "Failed to fetch dashboard statistics";
    }

    return res.json();
};