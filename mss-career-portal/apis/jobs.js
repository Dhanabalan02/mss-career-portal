// apis/jobs.js
// Mock API Wrapper for Jobs using jQuery deferred to mimic AJAX delays.

window.api = window.api || {};

api.jobs = {
    _data: [
        { id: 101, title: "Math Teacher", school: "Lady Andal School", experience: "3-5 years", status: "Open", type: "Full Time", location: "Chennai", date: "2026-03-10", applicants: 12 },
        { id: 102, title: "English Teacher (Middle School)", school: "Sir Mutha School", experience: "2-4 years", status: "Open", type: "Full Time", location: "Chennai", date: "2026-03-11", applicants: 8 },
        { id: 103, title: "Basketball Coach", school: "Lady Andal Open School", experience: "1-3 years", status: "Open", type: "Part Time", location: "Chennai", date: "2026-03-12", applicants: 3 },
        { id: 104, title: "High School Physics Teacher", school: "Sir & Lady M Venkatasubba Rao School", experience: "5+ years", status: "Open", type: "Full Time", location: "Chennai", date: "2026-03-08", applicants: 20 },
        { id: 105, title: "IB MYP Coordinator", school: "Lady Andal School", experience: "8+ years", status: "Open", type: "Contract", location: "Chennai", date: "2026-03-05", applicants: 5 }
    ],

    getFeaturedJobs: function () {
        var deferred = $.Deferred();
        setTimeout(() => {
            deferred.resolve(this._data.slice(0, 3));
        }, 500);
        return deferred.promise();
    },

    getAllJobs: function (filters) {
        var deferred = $.Deferred();
        setTimeout(() => {
            let filtered = this._data;
            if (filters && filters.school) {
                filtered = filtered.filter(j => j.school === filters.school);
            }
            if (filters && filters.type) {
                filtered = filtered.filter(j => j.type === filters.type);
            }
            if (filters && filters.search) {
                filtered = filtered.filter(j => j.title.toLowerCase().includes(filters.search.toLowerCase()));
            }
            deferred.resolve(filtered);
        }, 600);
        return deferred.promise();
    },

    getJobDetails: function (id) {
        var deferred = $.Deferred();
        setTimeout(() => {
            let job = this._data.find(j => j.id == id);
            if (job) deferred.resolve(job);
            else deferred.reject("Job not found");
        }, 400);
        return deferred.promise();
    },

    applyJob: function (formData) {
        var deferred = $.Deferred();
        setTimeout(() => {
            // Simulate success
            deferred.resolve({ status: 'success', message: 'Application submitted successfully' });
        }, 1200);
        return deferred.promise();
    }
};

api.dashboard = {
    getHRStats: function () {
        var deferred = $.Deferred();
        setTimeout(() => {
            deferred.resolve({
                totalJobs: 24,
                openPositions: 15,
                applicationsToday: 48,
                candidatesInPipeline: 120
            });
        }, 500);
        return deferred.promise();
    }
}
